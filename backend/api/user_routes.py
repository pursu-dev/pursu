'''
Facilitates user sign-up, user login, account deletion, etc.

Routes:
pursu.dev/api/user/google ==> get google client ID for email
pursu.dev/api/user/creds ==> user sign up and log in
pursu.dev/api/user/login ==> update user login timestamp
pursu.dev/api/user/info ==> user info insertion
pursu.dev/api/user/revoke ==> revoke user email access
pursu.dev/api/user/delete ==> delete user account
'''

# pylint: disable=E1101
import json
import requests
from apiclient import discovery
from oauth2client import client
from flask import request, jsonify, abort
import httplib2
from psycopg2 import sql

from api import start_watching, filters, get_credentials, stop_watching, add_to_state
from api import app, config, appConfig, create_creds
from api.utils import user_exists, transfer_user_account
from api.utils import add_filters, delete_old_user_filters, update_user_filters

SCOPES = ['https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.labels',
          'https://www.googleapis.com/auth/gmail.settings.basic'
          ]

GET_USER_DETAILS_QUERY = "SELECT uid, email, college FROM gmail JOIN users \
                           USING(uid) WHERE token={}"
REDEEMED_RECRUITERS_QUERY = "SELECT RR.rid from redeemed_recruiters RR INNER JOIN recruiters R \
                                  USING(rid) INNER JOIN companies C using(cid) \
                                  WHERE RR.uid = {} AND C.cid = {}"
RECRUITER_COLLEGE_QUERY = "SELECT rid, email, name FROM college_recruiter_link JOIN recruiters \
                            USING(rid) WHERE college={} AND cid={} \
                            AND rid NOT IN ("+REDEEMED_RECRUITERS_QUERY+") ORDER BY updated_at DESC"
RECRUITER_COMPANY_QUERY = "SELECT rid, email, R.name FROM recruiters R JOIN companies C \
                            USING(cid) WHERE cid={} AND rid NOT IN ("+REDEEMED_RECRUITERS_QUERY+") \
                            ORDER BY updated_at DESC"
REDEEM_RECRUITER_QUERY = "INSERT INTO redeemed_recruiters(uid, rid) VALUES({}, {})"
REDEEM_POINT_QUERY = "UPDATE referrals SET points=points-1, redemptions=redemptions+1 WHERE uid={}"

@app.route('/api/user/creds', methods=['POST'])
def app_pipeline():
    '''
    Route: /api/user/creds
    Description: Credentials API route for user initialization and sign-in
    '''
    auth_code = request.get_json()['token']
    client_id = request.get_json()['client_id']

    if not auth_code or not request.headers.get('X-Requested-With'):
        abort(403, 'Malformed gmail credentials')

    google_creds = config.get_google_project_credentials_for_client_id(appConfig, client_id)
    # Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_code(google_creds.client_id,
                                               google_creds.client_secret,
                                               SCOPES,
                                               auth_code)

    # Verify that user has provided necessary scopes
    if not user_granted_all_scopes(credentials):
        abort(401, "Insufficient scopes")

    # status: 200 = sign in, 201 = sign up
    try:
        refresh_token, user_status = init_user(credentials, google_creds.gcid)
        context = {'token': refresh_token}
    except Exception as err:
        abort(500, "Error in initializing user: {}".format(err))
    return jsonify(**context), user_status


@app.route('/api/user/login', methods=['POST'])
def record_login():
    '''
    Route: /api/user/login
    Description: User API route to update login timestamp in database
    '''
    body = request.get_json()
    token = body['token']
    context = {'token': token}

    query = sql.SQL("SELECT uid, email, label FROM gmail WHERE token={}").format(sql.Literal(token))
    res = appConfig.DB_CONN.execute_select_query(query)

    if res == []:
        abort(400, 'Invalid token')
    uid, email, label_id = res[0]

    if all([True for arg in [uid, email] if arg]) and user_exists(email):
        update_query = sql.SQL("UPDATE users SET login=CURRENT_TIMESTAMP WHERE uid={}").format(
            sql.Literal(uid))
        add_to_state(email, body)
        appConfig.DB_CONN.execute_update_query(update_query)
        # check if user is currently set to inactive
        query = sql.SQL("SELECT active FROM users WHERE uid={}").format(sql.Literal(uid))
        db_res = appConfig.DB_CONN.execute_select_query(query)
        if db_res == []:
            abort(400, "ERROR: Selecting if user {} was active failed".format(uid))
        active = int(db_res[0][0])
        if active == 0:
            creds = get_credentials(email, appConfig)
            update_user_filters(email, label_id)
            start_watching(creds, email, appConfig)
            update_query = sql.SQL(
                "UPDATE users SET active=1 WHERE uid={}").format(sql.Literal(uid))
            appConfig.DB_CONN.execute_update_query(update_query)
        return jsonify(**context), 200
    return jsonify(**context), 400


@app.route('/api/user/google', methods=['POST'])
def google_project_information():
    '''
    Route: /api/user/google
    Description: Grab google client id for given email
    '''
    body = request.get_json()
    email = body['email']
    client_id = config.get_google_project_credentials_for_email(appConfig, email).client_id
    context = {'client_id': client_id}
    return jsonify(**context), 200


@app.route('/api/user/info', methods=['POST'])
def store_user_info():
    '''
    Route: /api/user/info
    Description: User API route to write user information to database
    Validates referral information if code provided
    '''
    body = request.get_json()
    token = body['token']
    context = {'token': token}

    query = sql.SQL("SELECT uid, email FROM gmail WHERE token={}").format(sql.Literal(token))
    res = appConfig.DB_CONN.execute_select_query(query)

    if res == []:
        abort(400, 'Invalid token')
    uid, email = res[0][0], res[0][1]

    if all([True for arg in [uid, email] if arg]) and user_exists(email):
        if (body["college"] == "" or body["major"] == "" or body["year"] == ""
                or body["gender"] == "" or body["ethnicity"] == ""):
            abort(400, "One of college, major, year, gender, ethnicity missing in request:",
                  body["college"], body["major"], body["year"], body["gender"],
                  body["ethnicity"])
        add_to_state(email, body)
        queries = []
        update_query = sql.SQL("UPDATE users SET college={} WHERE uid={}").format(
            sql.Literal(body["college"]), sql.Literal(uid))
        queries.append(update_query)
        update_query = sql.SQL("UPDATE users SET major={} WHERE uid={}").format(
            sql.Literal(body["major"]), sql.Literal(uid))
        queries.append(update_query)
        update_query = sql.SQL("UPDATE users SET year={} WHERE uid={}").format(
            sql.Literal(body["year"]), sql.Literal(uid))
        queries.append(update_query)
        update_query = sql.SQL("UPDATE users SET consent={} WHERE uid={}").format(
            sql.Literal(int(body["consent"])), sql.Literal(uid))
        queries.append(update_query)
        update_query = sql.SQL("UPDATE users SET gender={} WHERE uid={}").format(
            sql.Literal(int(body["gender"])), sql.Literal(uid))
        queries.append(update_query)
        update_query = sql.SQL("UPDATE users SET ethnicity={} WHERE uid={}").format(
            sql.Literal(body["ethnicity"]), sql.Literal(uid))
        queries.append(update_query)

        for query in queries:
            appConfig.DB_CONN.execute_update_query(query)

        if body.get('referral') is not None and body.get('referral') != '':
            context['ref_success'], context['ref_name'] = validate_referral(body['referral'], email)
        return jsonify(**context), 200
    return jsonify(**context), 400


@app.route('/api/user/revoke', methods=['POST'])
def revoke_user_email_access():
    '''
    Route: /api/user/revoke
    Description: User API route to revoke pursu access to user email
    '''
    body = request.get_json()
    token = body['token']
    context = {'token': token}

    query = sql.SQL("SELECT uid, email FROM gmail WHERE token={}").format(sql.Literal(token))
    res = appConfig.DB_CONN.execute_select_query(query)

    if res == []:
        abort(400, 'Invalid token')
    uid, email = res[0][0]

    if all([True for arg in [email, uid] if arg]) and user_exists(email):
        add_to_state(email)
        revoke_pursu_email_access(uid=uid, user_email=email, token=token)
        return jsonify(**context), 200
    return jsonify(**context), 400


@app.route('/api/user/delete', methods=['POST'])
def delete_user_account():
    '''
    Route: /api/user/delete
    Description: User API route to delete user account
    '''
    body = request.get_json()
    token = body['token']
    context = {'token': token}

    query = sql.SQL("SELECT uid, email FROM gmail WHERE token={}").format(sql.Literal(token))
    res = appConfig.DB_CONN.execute_select_query(query)

    if res == []:
        abort(400, 'Invalid token')
    uid, email = res[0]

    if all([True for arg in [uid, email] if arg]) and user_exists(email):
        add_to_state(email)
        revoke_pursu_email_access(uid, email, token)
        delete_query = sql.SQL("DELETE FROM users WHERE uid={}").format(sql.Literal(uid))
        appConfig.DB_CONN.execute_delete_query(delete_query)
        return jsonify(**context), 200
    return jsonify(**context), 400


@app.route('/api/user/reset', methods=['POST'])
def reset_user_pipelines():
    '''
    Route: /api/user/reset
    Additional Arguments: reset_insights(int)
    Description: User API route to reset all pipelines for new recruiting cycle
    '''
    body = request.get_json()
    token = body['token']
    reset_insights = body['reset_insights']

    query = sql.SQL("SELECT uid, email FROM gmail WHERE token={}").format(sql.Literal(token))
    res = appConfig.DB_CONN.execute_select_query(query)

    if res == []:
        abort(400, 'Invalid token')
    uid, email = res[0]

    context = {'token': token, 'uid': uid}

    if all([True for arg in [uid, email] if arg]) and user_exists(email):
        # Set all pipelines as inactive
        query = sql.SQL("UPDATE pipelines SET active=0 WHERE uid={}").format(sql.Literal(uid))
        appConfig.DB_CONN.execute_update_query(query)
        if reset_insights:
            context['uid'] = transfer_user_account(uid, email)
        return jsonify(**context), 200
    return jsonify(**context), 400


@app.route('/api/user/redeem_recruiter_info', methods=['POST'])
def redeem_recruiter_info():
    '''
    Route: /api/user/redeem_recruiter_info
    Description: User API route to redeem a point to receive company recruiter contact information
    '''
    body = request.get_json()
    token = body['token']
    cid = body['cid']

    query = sql.SQL(GET_USER_DETAILS_QUERY).format(sql.Literal(token))
    res = appConfig.DB_CONN.execute_select_query(query)

    if res == []:
        abort(400, 'Invalid token')
    uid, email, college = res[0][0], res[0][1], res[0][2]

    context = {}

    if all([True for arg in [uid, email] if arg]) and user_exists(email):
        points_query = sql.SQL("SELECT points FROM referrals WHERE uid={}").format(sql.Literal(uid))
        points = appConfig.DB_CONN.execute_select_query(points_query)
        if points == []:
            # user does not exist in referrals table because they have not earned any points
            sql.SQL("INSERT INTO referrals(uid) VALUES({})").format(sql.Literal(uid))
            abort(400, 'User does not have enough points for redemption')
        res = int(points[0][0])
        if res == 0:
            abort(400, 'User does not have enough points for redemption')

        recruiter_university_query = sql.SQL(RECRUITER_COLLEGE_QUERY).format(sql.Literal(college),
                                                                             sql.Literal(cid),
                                                                             sql.Literal(uid),
                                                                             sql.Literal(cid))
        res = appConfig.DB_CONN.execute_select_query(recruiter_university_query)

        if res == []:
            recruiter_query = sql.SQL(RECRUITER_COMPANY_QUERY).format(sql.Literal(cid),
                                                                      sql.Literal(uid),
                                                                      sql.Literal(cid))
            res = appConfig.DB_CONN.execute_select_query(recruiter_query)

        if res == []:
            abort(400, 'No recruiters found for company')

        rid = res[0][0]
        recruiter_email = res[0][1]
        recruiter_name = res[0][2]

        redeem_recruiter_query = sql.SQL(REDEEM_RECRUITER_QUERY).format(sql.Literal(uid),
                                                                        sql.Literal(rid))
        appConfig.DB_CONN.execute_insert_query(redeem_recruiter_query)

        remove_point_query = sql.SQL(REDEEM_POINT_QUERY).format(sql.Literal(uid))
        appConfig.DB_CONN.execute_update_query(remove_point_query)

        context = {
            "rid": rid,
            "email": recruiter_email,
            "name": recruiter_name
        }

        return jsonify(**context), 200
    return jsonify(**context), 400


def init_user(credentials, gcid):
    '''
    Function to initialize user.
    '''
    _, refresh_token, name, email = parse_credentials(credentials)
    encrypted_refresh_token = config.encrypt_token(refresh_token, appConfig)
    add_to_state(email)
    if user_exists(email) == 0:
        # user does not exist
        filt_vers = filters.get_latest_filter_version(appConfig)

        # create label for all new users, filter only for beta users
        new_label_id = create_label(credentials, email)

        # We need to keep the RETURNING statement here to assure we select correct user
        sql_query = sql.SQL("INSERT INTO users(name, filt_version) VALUES({}, {}) \
            RETURNING uid;").format(sql.Literal(name), sql.Literal(filt_vers))
        add_filters(credentials, email, new_label_id)
        start_watching(credentials, email, appConfig)
        uid = appConfig.DB_CONN.execute_insert_return_query(sql_query)

        sql_query = sql.SQL("INSERT INTO gmail(uid, email, token, label, gcid) \
            VALUES({}, {}, {}, {}, {})").format(sql.Literal(uid), sql.Literal(email),
                                                sql.Literal(encrypted_refresh_token),
                                                sql.Literal(new_label_id),
                                                sql.Literal(gcid))
        appConfig.DB_CONN.execute_insert_query(sql_query)
        return encrypted_refresh_token, 201
    if encrypted_refresh_token is not None:
        if not token_is_valid(refresh_token, email):
            return None, 403

        # user exists but old token expired
        sql_query = sql.SQL("UPDATE gmail SET token = {} WHERE email = {}").format(
            sql.Literal(encrypted_refresh_token), sql.Literal(email))
        appConfig.DB_CONN.execute_update_query(sql_query)
        return encrypted_refresh_token, 200
    # needed for frontend to caching of sign in
    return config.get_refresh_token(email=email, decrypted=False, appConfig=appConfig), 200


def parse_credentials(credentials):
    '''
    Function to parse credentials.
    '''
    access_token = credentials.access_token
    refresh_token = credentials.refresh_token
    name = credentials.id_token['name']
    email = credentials.id_token['email']
    return access_token, refresh_token, name, email


def revoke_pursu_email_access(uid, user_email, token):
    '''
    Helper function to revoke pursu access to user email
    '''
    creds = get_credentials(user_email, appConfig)
    stop_watching(creds, user_email)

    # Set user as inactive
    update_query = sql.SQL("UPDATE users SET active=0 WHERE uid={}").format(sql.Literal(uid))
    appConfig.DB_CONN.execute_update_query(update_query)

    # Remove filters
    query = sql.SQL("SELECT label FROM gmail WHERE token={}").format(sql.Literal(token))
    res = appConfig.DB_CONN.execute_select_query(query)
    if res == []:
        print("ERROR IN REVOKING EMAIL ACCESS FOR {}".format(user_email))
        return
    label_id = res[0][0]
    delete_old_user_filters(creds, user_email, label_id)

    # Remove pursu-label
    delete_label(creds, user_email, label_id)

    # Revoke email access
    requests.post('https://oauth2.googleapis.com/revoke',
                  params={'token': creds.access_token},
                  headers={'content-type': 'application/x-www-form-urlencoded'}
                  )


def create_label(creds, email):
    '''
    Function to create a label.
    '''
    _http_auth = creds.authorize(httplib2.Http())
    gmail = discovery.build('gmail', 'v1', credentials=creds)

    reqs = {
        'labelListVisibility': 'labelHide',
        'messageListVisibility': 'hide',
        'name': 'pursu-label'
    }
    label = check_for_existing_label(gmail)
    if label is None:
        label = gmail.users().labels().create(userId=email, body=reqs).execute()
    return label['id']


def delete_label(creds, email, label_id):
    '''
    Function to delete pursu-generated label.
    '''
    _http_auth = creds.authorize(httplib2.Http())
    gmail = discovery.build('gmail', 'v1', credentials=creds)
    gmail.users().labels().delete(userId=email, id=label_id).execute()


def check_for_existing_label(gmail):
    '''
    Function that checks if user has an existing label
    '''
    user_labels = gmail.users().labels().list(userId='me').execute()
    for label in user_labels['labels']:
        if label['name'] == 'pursu-label':
            return label
    return None


def user_granted_all_scopes(creds):
    '''
    Verify that new user granted all necessary scopes
    '''
    _http_auth = creds.authorize(httplib2.Http())
    hp = httplib2.Http()
    out = hp.request("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}".format(
        creds.access_token))
    scopes = set(json.loads(out[1])['scope'].split())
    return scopes.issuperset(set(SCOPES))


def token_is_valid(refresh_token, email):
    '''
    Ensure that new refresh token is valid for user email
    '''
    creds = create_creds(refresh_token, email, appConfig)
    if creds is not None:
        hp = httplib2.Http()
        out = hp.request("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}".format(
            creds.access_token))
        token_response = json.loads(out[1])
        return 'email' in token_response and token_response['email'] == email
    return False

def validate_referral(referral_code, user_email):
    '''
    Validate referral code for sign-up + reward points
    Parameters:
        - referral_code: The email of the referring user
    Returns: (success, referring_name)
    '''
    # Ensure user is not referring themself
    if referral_code == user_email:
        return False, ""

    query = sql.SQL("SELECT uid, name FROM users \
        JOIN gmail G USING(uid) WHERE G.email={}").format(sql.Literal(referral_code))
    res = appConfig.DB_CONN.execute_select_query(query)
    if res != []:
        uid, name = res[0]

        # Upsert referral row
        query = sql.SQL(
            "INSERT INTO referrals(uid, points, redemptions) VALUES({}, 1, 0) \
            ON CONFLICT (uid) \
            DO UPDATE SET points = referrals.points + 1").format(sql.Literal(uid))
        appConfig.DB_CONN.execute_insert_query(query)
        return True, name
    return False, ""
