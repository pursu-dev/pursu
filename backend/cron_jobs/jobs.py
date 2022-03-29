'''
Module for Email Jobs
'''
import httplib2
from oauth2client import client
from apiclient import discovery
from psycopg2 import sql

from cron_jobs import config

TOKEN_URI = 'https://oauth2.googleapis.com/token'

# pylint: disable=E1101

def renew_watch(appConfig):
    '''
    Function for renew watching
    '''
    sql_query = sql.SQL("SELECT uid FROM users WHERE active=1")
    users_to_watch = appConfig.DB_CONN.execute_select_query(sql_query)
    for user in users_to_watch:
        sql_query = sql.SQL("SELECT email FROM gmail WHERE uid={}").format(sql.Literal(user[0]))
        db_res = appConfig.DB_CONN.execute_select_query(sql_query)
        my_email = db_res[0][0] if db_res != [] else None
        if my_email is not None:
            creds = get_credentials(my_email, appConfig)
            if creds is not None:
                stop_watching(creds, my_email)
                start_watching(creds, my_email, appConfig)
            else:
                sql_query = sql.SQL("UPDATE users SET active=0 WHERE uid={}").format(
                    sql.Literal(user[0]))
                appConfig.DB_CONN.execute_update_query(sql_query)


def stop_watching_inactive_users(appConfig):
    '''
    Function to stop watching all inactive users
    '''
    # Notify users who are close to inactive status
    sql_query = sql.SQL(
        "SELECT uid, name FROM users WHERE login <= NOW() - INTERVAL '11 DAY' AND \
             login > NOW() - INTERVAL '12 DAY' AND active=1")
    users = appConfig.DB_CONN.execute_select_query(sql_query)

    for row in users:
        uid = row[0]
        name = row[1]
        sql_query = sql.SQL("SELECT email FROM gmail WHERE uid={}").format(sql.Literal(uid))
        email = appConfig.DB_CONN.execute_select_query(sql_query)[0][0]
        # Had to concat strings like this to avoid malformed email messages
        config.send_email(
            appConfig,
            email,
            'Pursu Misses You, ' + name.split()[0] + '!',
            'You have not logged in to your Pursu dashboard in almost 2 weeks. We miss you!' +
            '\n\nDue to our server costs, we will stop automatically updating your pipelines ' +
            'if you do not log in within the next three days. No worries, we will ' +
            'automatically begin updating again if you log in after this deadline.' +
            '\n\nThanks for understanding, we hope to see you soon at https://pursu.dev/.')

    # Free resources for newly inactive users
    sql_query = sql.SQL(
        "SELECT uid FROM users WHERE login < NOW() - INTERVAL '14 DAY' AND active=1")
    users = appConfig.DB_CONN.execute_select_query(sql_query)

    for uid in users:
        uid = uid[0]
        sql_query = sql.SQL("SELECT email, label FROM gmail WHERE uid={}").format(sql.Literal(uid))
        db_res = appConfig.DB_CONN.execute_select_query(sql_query)
        email, label_id = db_res[0] if len(db_res) > 0 else None, None
        if email is None or label_id is None:
            continue
        creds = get_credentials(email, appConfig)
        delete_old_user_filters(creds, label_id)
        stop_watching(creds, email)
        update_query = sql.SQL("UPDATE users SET active=0 WHERE uid={}").format(sql.Literal(uid))
        appConfig.DB_CONN.execute_update_query(update_query)

def create_creds(refresh_token, email, appConfig):
    '''
    Generate creds object from refresh token
    '''
    try:
        google_creds = config.get_google_project_credentials_for_email(appConfig, email)
        creds = client.OAuth2Credentials(access_token=None,
                                         client_id=google_creds.client_id,
                                         client_secret=google_creds.client_secret,
                                         refresh_token=refresh_token, token_expiry=None,
                                         token_uri=TOKEN_URI, user_agent=None, revoke_uri=None)
        _http_auth = creds.authorize(httplib2.Http())
        creds.refresh(httplib2.Http())
        return creds
    except Exception as _err:
        print("INVALID CREDENTIALS FOR {}".format(email))
        return None


def get_credentials(email, appConfig):
    '''
    Function to get credentials
    '''
    refresh_token = config.get_refresh_token(email=email, decrypted=True, appConfig=appConfig)
    return create_creds(refresh_token, email, appConfig)

def start_watching(creds, email, appConfig):
    '''
    Function to start watching email job
    '''
    # Call Google API
    _http_auth = creds.authorize(httplib2.Http())
    gmail = discovery.build('gmail', 'v1', credentials=creds)

    # This should cover all normal labels
    # BUG: Issue arises if user has automatic labelling that skips inbox
    IGNORE_LABELS = ['SENT', 'DRAFT', 'TRASH', 'SPAM']

    # We need to use this convoluted method because of gmail API bugs in including labels
    # TODO: Query on just the user's labelID
    request = {
        'labelIds': IGNORE_LABELS,
        'labelFilterAction': 'exclude',
        'topicName': config.get_google_project_credentials_for_email(appConfig, email).topic
    }
    results = gmail.users().watch(userId=email, body=request).execute()

    # update history id in database
    sql_query = sql.SQL("UPDATE gmail SET history={} WHERE email={}").format(
        sql.Literal(results['historyId']), sql.Literal(email))
    appConfig.DB_CONN.execute_update_query(sql_query)


def stop_watching(creds, email):
    '''
    Function to stop watching the email job
    '''
    try:
        gmail = discovery.build('gmail', 'v1', credentials=creds)
        gmail.users().stop(userId=email).execute()
    except Exception as err:
        print(err)


def stop_inactive_and_renew(appConfig, app):
    '''
    Entry point for renew watch functionality
    '''
    app.logger.debug("Began renew watch cron job")
    try:
        stop_watching_inactive_users(appConfig)
    except Exception as exp:
        app.logger.error("Stop watching failed: {}".format(exp))
    try:
        renew_watch(appConfig)
    except Exception as exp:
        app.logger.error("Renew watch call failed: {}".format(exp))
    app.logger.debug("Finished renew watch cron job")


def delete_old_user_filters(creds, label_id):
    '''
    Function to delete old pursu-generated filters for passed-in user email
    '''
    gmail = discovery.build('gmail', 'v1', credentials=creds)
    filts = gmail.users().settings().filters().list(userId='me').execute()

    for filt in filts['filter']:
        if 'action' in filt and 'addLabelIds' in filt['action']:
            if label_id in filt['action']['addLabelIds']:
                gmail.users().settings().filters().delete(userId='me', id=filt['id']).execute()
