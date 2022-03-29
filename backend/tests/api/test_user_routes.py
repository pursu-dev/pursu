from shared.google_credentials import GoogleCredentials
import pytest
import json
import datetime
import pytz
from email_analysis import LABELS_TO_CATEGORIES, CATEGORIES_TO_LABELS  # pylint: disable=E0401
import api.user_routes as main_pipeline  # pylint: disable=E0401
import helper  # pylint: disable=E0401


def test_api_edit_user_info(main_api, db_conn):
    '''
    Test user info editing route
    '''
    helper.create_test_user_and_email(db_conn=db_conn)

    # Gender: 0 == Male, 1 == Female, 2 == Non-binary, 3 == Undisclosed
    data = {
        'token': 'token',
        'college': 'University of Michigan',
        'major': 'Computer Science',
        'year': 2022,
        'gender': 0,
        'ethnicity': 'Asian',
        'consent': True,
        'referral': ''
    }
    status = main_api.post('/api/user/info', json=data).status_code

    query = "SELECT college, major, year, consent, gender, ethnicity \
        FROM users WHERE name='Joe Schmoe';"
    db_res = helper.execute_test_query(db_conn, query)

    assert status == 200
    assert list(db_res[0]) == ['University of Michigan', 'Computer Science', 2022, True, 0, 'Asian']


def test_api_delete_user_account(main_api, db_conn, mocker):
    '''
    Test route to delete a user account. Ensure that route
    delete all user-associated data & revokes gmail access
    '''
    my_email = 'jschmoe@gmail.com'
    my_token = 'token'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email, token=my_token)
    cid = helper.create_test_company(db_conn=db_conn)
    _pid = helper.create_test_pipeline(db_conn=db_conn, uid=uid, cid=cid)

    revoke_access_call = mocker.patch(
        'api.user_routes.revoke_pursu_email_access',
        return_value=None)

    data = {
        'token': my_token
    }

    main_api.post('/api/user/delete', json=data).status_code

    query1 = "SELECT token FROM gmail WHERE uid={}".format(uid)
    query2 = "SELECT name FROM users WHERE uid={}".format(uid)
    query3 = "SELECT pid FROM pipelines WHERE uid={}".format(uid)

    email_res = helper.execute_test_query(db_conn, query1)
    name_res = helper.execute_test_query(db_conn, query2)
    pipeline_res = helper.execute_test_query(db_conn, query3)

    revoke_access_call.assert_called_once_with(uid, my_email, my_token)
    assert list(email_res) == []
    assert list(name_res) == []
    assert list(pipeline_res) == []


def test_api_revoke_user_email_access(main_api, db_conn, mocker):
    '''
    Test route to revoke gmail access for user
    '''
    my_email = 'jschmoe@gmail.com'
    my_token = 'token'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email, token=my_token)

    revoke_access_call = mocker.patch(
        'api.user_routes.revoke_pursu_email_access',
        return_value=None)

    data = {
        'token': my_token
    }

    main_api.post('/api/user/delete', json=data).status_code
    revoke_access_call.assert_called_once_with(uid, my_email, my_token)


def test_api_login_invalid_token_returns_error(main_api, db_conn):
    '''
    Test route for user login to ensure that invalid tokens are rejected
    '''
    invalid_token = 'notMyToken'
    _uid = helper.create_test_user_and_email(
        db_conn,
        name='Joe Schmoe',
        email='jschmoe@gmail.com',
        token='myToken')

    data = {'token': invalid_token}
    status = main_api.post('/api/user/login', json=data).status_code

    assert status == 400


def test_api_login_sets_login_timestamps_for_active_users(main_api, db_conn, mocker):
    '''
    Test route for user login to ensure that it sets the timestamp of user login
    '''
    TIME_EPSILON = datetime.timedelta(seconds=10)

    start_watching_call = mocker.patch('api.user_routes.start_watching')
    my_name = 'Joe Schmoe'
    my_email = 'jschmoe@gmail.com'
    my_token = 'token'

    # As defined in schema, default behavior is to set user as actively watched
    uid = helper.create_test_user_and_email(db_conn, name=my_name, email=my_email, token=my_token)
    data = {'token': my_token}

    expected_timestamp = pytz.utc.localize(datetime.datetime.utcnow())
    # Hard-code existing timestamp to check that it is properly updated
    query = "UPDATE users SET login='{}' WHERE uid={};".format(
        expected_timestamp - TIME_EPSILON, uid)
    helper.execute_test_query(db_conn, query)
    status = main_api.post('/api/user/login', json=data).status_code

    query = "SELECT login FROM users WHERE uid={};".format(uid)
    my_timestamp = helper.execute_test_query(db_conn, query)[0][0]
    #my_timestamp = datetime.datetime.strptime(my_timestamp, '%Y-%m-%d %H:%M:%S')

    assert start_watching_call.never_called()
    assert my_timestamp - expected_timestamp < TIME_EPSILON
    assert status == 200


def test_api_login_starts_watching_on_invactive_users(main_api, db_conn, mocker):
    '''
    Test route for user login to ensure that it correctly starts watching a logged-in user
    whose account was previously inactive
    '''
    my_name = 'Joe Schmoe'
    my_email = 'jschmoe@gmail.com'
    my_token = 'token'
    my_creds = 'creds'
    my_label = 'label'

    start_watching_call = mocker.patch('api.user_routes.start_watching', return_value=None)
    add_filters_call = mocker.patch('api.user_routes.update_user_filters', return_value=None)
    get_credentials_call = mocker.patch('api.user_routes.get_credentials', return_value=my_creds)

    uid = helper.create_test_user_and_email(
        db_conn,
        name=my_name,
        email=my_email,
        token=my_token,
        label=my_label)
    query = "UPDATE users SET active=0 WHERE uid={};".format(uid)
    helper.execute_test_query(db_conn, query)

    data = {'token': my_token}

    status = main_api.post('/api/user/login', json=data).status_code
    query = "SELECT active FROM users WHERE uid={};".format(uid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    get_credentials_call.assert_called_once_with(my_email, main_pipeline.appConfig)
    start_watching_call.assert_called_once_with(my_creds, my_email, main_pipeline.appConfig)
    add_filters_call.assert_called_once_with(my_email, my_label)
    assert status == 200
    assert list(db_res) == [1]


def test_api_login_does_not_watch_for_manual_users(main_api, db_conn, mocker):
    '''
    Test route for user login to ensure that it doest not start watching a logged-in user
    if the user previously chose to revoke gmail account access
    '''

    my_name = 'Joe Schmoe'
    my_email = 'jschmoe@gmail.com'
    my_token = 'token'
    my_creds = 'creds'

    start_watching_call = mocker.patch('api.user_routes.start_watching', return_value=None)
    mocker.patch('api.user_routes.get_credentials', return_value=my_creds)

    uid = helper.create_test_user_and_email(db_conn, name=my_name, email=my_email, token=my_token)
    query = "UPDATE users SET active=-1 WHERE uid={};".format(uid)
    helper.execute_test_query(db_conn, query)

    data = {'token': my_token}

    status = main_api.post('/api/user/login', json=data).status_code
    query = "SELECT active FROM users WHERE uid={};".format(uid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    start_watching_call.assert_not_called()
    assert status == 200
    assert list(db_res) == [-1]


def test_revoke_pursu_email_access(main_api, db_conn, mocker):
    '''
    Unit test to ensure that revoking pursu email access works properly
    '''
    my_email = 'jschmoe@gmail.com'
    my_token = 'token'
    my_label_id = 'label'
    uid = helper.create_test_user_and_email(
        db_conn=db_conn,
        email=my_email,
        token=my_token,
        label=my_label_id)

    expected_params = {
        'token': my_token
    }

    expected_headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }

    creds = mocker.MagicMock()
    creds.access_token = my_token
    creds_call = mocker.patch('api.user_routes.get_credentials', return_value=creds)
    stop_watch_call = mocker.patch('api.user_routes.stop_watching', return_value=None)
    delete_filt_call = mocker.patch('api.user_routes.delete_old_user_filters', return_value=None)
    delete_label_call = mocker.patch('api.user_routes.delete_label', return_value=None)
    revoke_call = mocker.patch('requests.post', return_value=None)

    main_pipeline.revoke_pursu_email_access(uid, my_email, my_token)

    creds_call.assert_called_once()
    stop_watch_call.assert_called_once_with(creds, my_email)
    delete_filt_call.assert_called_once_with(creds, my_email, my_label_id)
    delete_label_call.assert_called_once_with(creds, my_email, my_label_id)
    revoke_call.assert_called_once_with(
        'https://oauth2.googleapis.com/revoke',
        params=expected_params,
        headers=expected_headers)


def test_reset_user_pipelines_retain_insights(main_api, db_conn, mocker):
    '''
    Test route for resetting only user pipelines for new recruiting cycle
    '''
    my_email = 'jschmoe@gmail.com'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email)
    cid = helper.create_test_company(db_conn=db_conn)
    pid = helper.create_test_pipeline(db_conn, uid, cid)

    data = {
        'token': 'token',
        'reset_insights': False
    }

    new_uid = 2
    transfer_user = mocker.patch('api.user_routes.transfer_user_account', return_value=new_uid)

    response = main_api.post('/api/user/reset', json=data)
    status = response.status_code
    data = json.loads(response.data.decode('utf-8'))

    query = "SELECT active FROM pipelines WHERE pid={}".format(pid)
    db_res = helper.execute_test_query(db_conn, query)

    transfer_user.assert_not_called()
    assert status == 200
    assert data == {'token': 'token', 'uid': uid}
    assert int(db_res[0][0]) == 0


def test_reset_user_pipelines_reset_insights(main_api, db_conn, mocker):
    '''
    Test route for resetting user pipelines and insights for new recruiting cycle
    '''
    my_email = 'jschmoe@gmail.com'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email)
    cid = helper.create_test_company(db_conn=db_conn)
    pid = helper.create_test_pipeline(db_conn, uid, cid)

    data = {
        'token': 'token',
        'reset_insights': True
    }

    new_uid = 2
    transfer_user = mocker.patch('api.user_routes.transfer_user_account', return_value=new_uid)

    response = main_api.post('/api/user/reset', json=data)
    status = response.status_code
    data = json.loads(response.data.decode('utf-8'))

    query = "SELECT active FROM pipelines WHERE pid={}".format(pid)
    db_res = helper.execute_test_query(db_conn, query)

    transfer_user.assert_called_once_with(uid, my_email)
    assert status == 200
    assert data == {'token': 'token', 'uid': new_uid}
    assert int(db_res[0][0]) == 0

def test_api_get_google_project_information(main_api, db_conn, mocker):
    '''
    Basic test for google project route
    '''
    google_creds = GoogleCredentials(gcid=1,project_id='pid', client_id='cid', 
                                     client_secret='secret', topic='topic', has_space=True)
    get_creds = mocker.patch('api.config.get_google_project_credentials_for_email', 
                             return_value=google_creds)
    my_email = 'jschmoe@gmail.com'
    helper.create_test_user_and_email(db_conn=db_conn, email=my_email)
    data = {
        'email': my_email
    }
    response = main_api.post('/api/user/google', json=data)
    status = response.status_code
    data = json.loads(response.data.decode('utf-8')) 

    get_creds.assert_called_once_with(main_pipeline.appConfig, my_email)
    assert status == 200
    assert data == {'client_id': 'cid'}

def test_no_redeemable_recruiter_for_company(main_api, db_conn, mocker):
    '''
    Test route for redeeming a point and company has no recruiters in db
    '''
    my_email = 'jschmoe@gmail.com'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email)
    helper.award_points_to_new_user(db_conn=db_conn, uid=uid, num_points=1)
    cid = helper.create_test_company(db_conn=db_conn)

    data = {
        'token': 'token',
        'cid': cid
    }

    response = main_api.post('/api/user/redeem_recruiter_info', json=data)
    status = response.status_code
    assert status == 400

    query = "SELECT COUNT(*) FROM redeemed_recruiters WHERE uid={}".format(uid)
    db_res = helper.execute_test_query(db_conn, query)
    assert int(db_res[0][0]) == 0

    query = "SELECT points, redemptions FROM referrals WHERE uid={}".format(uid)
    db_res = helper.execute_test_query(db_conn, query)
    assert db_res == [(1, 0)]


def test_reedem_with_zero_points(main_api, db_conn, mocker):
    '''
    Test route for redeeming a point and user does not have any points
    '''
    my_email = 'jschmoe@gmail.com'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email)
    # ensure row is created
    helper.award_points_to_new_user(db_conn=db_conn, uid=uid, num_points=0)
    cid = helper.create_test_company(db_conn=db_conn)

    data = {
        'token': 'token',
        'cid': cid
    }

    response = main_api.post('/api/user/redeem_recruiter_info', json=data)
    status = response.status_code
    assert status == 400

    query = "SELECT COUNT(*) FROM redeemed_recruiters WHERE uid={}".format(uid)
    db_res = helper.execute_test_query(db_conn, query)
    assert int(db_res[0][0]) == 0

    query = "SELECT points, redemptions FROM referrals WHERE uid={}".format(uid)
    db_res = helper.execute_test_query(db_conn, query)
    assert db_res == [(0, 0)]


def test_reedem_recruiter_happy_path(main_api, db_conn, mocker):
    '''
    Test route for redeeming a point for a recruiter
    Case 1: Match for college and company
    Case 2: No match for college but match for company

    User jschmoe@gmail.com is redeeming two points for recruiters at Google and Facebook.
    User schmoe@gmail.com goes to the same college and has recruited with Google.
    '''
    email1 = 'jschmoe@gmail.com'
    email2 = 'schmoe@gmail.com'
    uid1 = helper.create_test_user_and_email(db_conn=db_conn, email=email1)
    uid2 = helper.create_test_user_and_email(
        db_conn=db_conn, email=email2, token='token2', name='Schmoe')
    helper.award_points_to_new_user(db_conn=db_conn, uid=uid1, num_points=2)
    google_cid = helper.create_test_company(db_conn=db_conn, name='Google')
    facebook_cid = helper.create_test_company(db_conn=db_conn, name='Facebook')

    helper.create_test_recruiter(
        db_conn=db_conn,
        cid=google_cid,
        name='Bad Google Recruiter',
        email='badgooglerecruiter@google.com')
    rid = helper.create_test_recruiter(
        db_conn=db_conn,
        cid=google_cid,
        name='Best Google Recruiter',
        email='bestgooglerecruiter@google.com')
    helper.create_test_recruiter(
        db_conn=db_conn,
        cid=google_cid,
        name='Worst Google Recruiter',
        email='worstgooglerecruiter@google.com')
    helper.create_test_college_recruiter_link(db_conn, rid=rid)

    data = {
        'token': 'token',
        'cid': google_cid
    }

    response = main_api.post('/api/user/redeem_recruiter_info', json=data)
    status = response.status_code
    data = json.loads(response.data.decode('utf-8'))

    assert status == 200
    assert data['rid'] == rid

    email3 = 'moe@gmail.com'
    uid3 = helper.create_test_user_and_email(
        db_conn=db_conn,
        email=email3,
        college='UC Berkeley',
        token='token3',
        name='Moe')

    rid2 = helper.create_test_recruiter(
        db_conn=db_conn,
        cid=facebook_cid,
        name='Decent Facebook Recruiter',
        email='decentfacebookrecruiter@google.com')
    helper.create_test_college_recruiter_link(
        db_conn=db_conn,
        rid=rid2,
        college='UC Berkeley')

    data = {
        'token': 'token',
        'cid': facebook_cid
    }

    response = main_api.post('/api/user/redeem_recruiter_info', json=data)
    status = response.status_code
    data = json.loads(response.data.decode('utf-8'))

    assert status == 200
    assert data['rid'] == rid2

    query = "SELECT rid FROM redeemed_recruiters WHERE uid={}".format(uid1)
    db_res = helper.execute_test_query(db_conn, query)
    assert db_res == [(rid, ), (rid2, )]

    query = "SELECT points, redemptions FROM referrals WHERE uid={}".format(uid1)
    db_res = helper.execute_test_query(db_conn, query)
    assert db_res == [(0, 2)]

def test_redeeming_redeemed_recruiter(main_api, db_conn, mocker):
    '''
    Test route for redeeming a recruiter that has already been redeemed by the user.
    '''
    email1 = 'jschmoe@gmail.com'
    uid1 = helper.create_test_user_and_email(db_conn=db_conn, email=email1)
    helper.award_points_to_new_user(db_conn=db_conn, uid=uid1, num_points=2)
    google_cid = helper.create_test_company(db_conn=db_conn, name='Foogle')

    rid = helper.create_test_recruiter(
        db_conn=db_conn,
        cid=google_cid,
        name='Best Google Recruiter',
        email='bestgooglerecruiter@google.com')
    helper.create_test_college_recruiter_link(db_conn, rid=rid)

    data = {
        'token': 'token',
        'cid': google_cid
    }

    response = main_api.post('/api/user/redeem_recruiter_info', json=data)
    status = response.status_code
    data = json.loads(response.data.decode('utf-8'))

    assert status == 200
    assert data['rid'] == rid

    data = {
        'token': 'token',
        'cid': google_cid
    }

    response = main_api.post('/api/user/redeem_recruiter_info', json=data)
    status = response.status_code

    assert status == 400


def test_validate_referral_success_no_existing_entry(main_api, db_conn):
    '''
    Test validation of successful referral code for user without database entry
    Validation should set point value to 1 for new entry
    '''
    user_email = 'joe@gmail.com'
    referral_code = 'jschmoe@gmail.com'
    my_name = 'Joe Schmoe'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=referral_code, name=my_name)

    success, name = main_pipeline.validate_referral(referral_code, user_email)

    # Validate referral entry inserted + points incremented
    query = "SELECT points FROM referrals WHERE uid={}".format(uid)
    db_res = helper.execute_test_query(db_conn, query)[0][0]

    assert success
    assert name == my_name
    assert db_res == 1


def test_validate_referral_success_with_existing_entry(main_api, db_conn):
    '''
    Test validation of successful referral code for user with existing database entry
    Validation should increment point value
    '''
    user_email = 'joe@gmail.com'
    referral_code = 'jschmoe@gmail.com'
    my_name = 'Joe Schmoe'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=referral_code, name=my_name)
    helper.create_test_referral_entry(db_conn, uid, points=1)

    success, name = main_pipeline.validate_referral(referral_code, user_email)

    # Validate referral entry inserted + points incremented
    query = "SELECT points FROM referrals WHERE uid={}".format(uid)
    db_res = helper.execute_test_query(db_conn, query)[0][0]

    assert success
    assert name == my_name

    # Ensure that points have been incremented
    assert db_res == 2


def test_validate_referral_failure(main_api, db_conn):
    '''
    Test validation of failing referral code 
    '''
    user_email = 'joe@gmail.com'
    referral_code = 'jschmoe@gmail.com'

    # No user has been created with this email, so referral should fail
    success, name = main_pipeline.validate_referral(referral_code, user_email)

    # Validate referral entry not inserted
    query = "SELECT COUNT(*) FROM referrals;"
    db_res = helper.execute_test_query(db_conn, query)[0][0]

    assert not success
    assert db_res == 0


def test_validate_referral_self_validation(main_api, db_conn):
    '''
    Test validation of failing referral code 
    '''
    referral_code = 'jschmoe@gmail.com'

    # No user has been created with this email, so referral should fail
    success, name = main_pipeline.validate_referral(referral_code, referral_code)

    # Validate referral entry not inserted
    query = "SELECT COUNT(*) FROM referrals;"
    db_res = helper.execute_test_query(db_conn, query)[0][0]

    assert not success
    assert db_res == 0

def test_init_user_basic(main_api, db_conn, mocker):
    '''
    Ensure that all gmail table fields are properly initialized for new user sign-up
    '''
    # Create google project
    target_gcid = helper.create_test_google_project(
        db_conn, 
        main_pipeline.appConfig, 
        client_id='test_id2', 
        client_secret='test_secret2', 
        project_id='pid', 
        topic='topic'
    )

    mocker.patch(
        "api.user_routes.parse_credentials",
        return_value=(None, 'refresh_token', 'name', 'email')
    )
    mocker.patch("api.user_routes.config.encrypt_token", return_value='encrypted_token')
    mocker.patch("api.user_routes.add_to_state", return_value=None)
    mocker.patch("api.user_routes.filters.get_latest_filter_version", return_value=1)
    mocker.patch("api.user_routes.create_label", return_value=1)
    mocker.patch("api.user_routes.add_filters", return_value=None)
    mocker.patch("api.user_routes.start_watching", return_value=None)

    creds = mocker.MagicMock()

    # Initialize new user
    main_pipeline.init_user(creds, target_gcid)

    out = helper.execute_test_query(db_conn, "SELECT email,token,label,gcid FROM gmail \
        WHERE email='email'")[0]
    assert list(out) == ['email', 'encrypted_token', '1', target_gcid]
