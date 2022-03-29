''' Unit tests for various functions in module jobs.py '''

import datetime
import helper  # pylint: disable=E0401
from cron_jobs import jobs  # pylint: disable=E0401

def test_start_watching_call_excludes_main_gmail_labels(mocker, db_conn, appConfig):
    '''
    Test start watching function to ensure main gmail-generated labels are ignored
    '''
    my_pursu_label = 'Label_2'
    my_email = 'jschmoe@gmail.com'
    my_history_id = '10'

    google_proj_creds = mocker.MagicMock()
    google_proj_creds.topic = "pursu_test_topic"
    mocker.patch('cron_jobs.config.get_google_project_credentials_for_email', return_value=google_proj_creds)

    creds = mocker.MagicMock()
    gmail = mocker.MagicMock()
    
    discovery_client = mocker.patch('apiclient.discovery.build', return_value=gmail)
    creds.authorize.return_value = None
    gmail.users().watch().execute.return_value = {'historyId': my_history_id}

    uid = helper.create_test_user_and_email(db_conn=db_conn, label=my_pursu_label, email=my_email)

    jobs.start_watching(creds=creds, email=my_email, appConfig=appConfig)

    expected_request = {
        'labelIds': ['SENT', 'DRAFT', 'TRASH', 'SPAM'],
        'labelFilterAction': 'exclude',
        'topicName': 'pursu_test_topic'
    }

    query = "SELECT history FROM gmail WHERE uid={}".format(uid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    discovery_client.assert_called_once_with('gmail', 'v1', credentials=creds)
    gmail.users().watch.assert_called_with(userId=my_email, body=expected_request)
    gmail.users().watch().execute.assert_called_once_with()
    assert list(db_res) == [my_history_id]


def test_stop_watching(db_conn, mocker):
    '''
    Tests that stop watching functionality properly queries gmail API
    '''
    my_email = 'jschmoe@gmail.com'
    creds = mocker.MagicMock()
    gmail = mocker.MagicMock()
    discovery_client = mocker.patch('apiclient.discovery.build', return_value=gmail)

    jobs.stop_watching(creds, my_email)

    discovery_client.assert_called_once_with('gmail', 'v1', credentials=creds)
    gmail.users().stop.assert_called_once_with(userId=my_email)
    gmail.users().stop().execute.assert_called_once_with()


def test_renew_watch_iterates_through_all_users(db_conn, mocker, appConfig):
    '''
    Test that renew watch stops and starts watch for all users
    '''

    my_first_email = 'jschmoe@gmail.com'
    my_first_name = 'Joe Schmoe'
    my_second_email = 'pursufounder@gmail.com'
    my_second_name = 'Pursu Founder'
    my_creds = 'aCredentialsObject'

    helper.create_test_user_and_email(
        db_conn=db_conn,
        email=my_first_email,
        name=my_first_name,
        token='aFirstToken')
    helper.create_test_user_and_email(
        db_conn=db_conn,
        email=my_second_email,
        name=my_second_name,
        token='aSecondToken')

    creds_call = mocker.patch('cron_jobs.jobs.get_credentials', return_value=my_creds)
    stop_watch = mocker.patch('cron_jobs.jobs.stop_watching', return_value=None)
    start_watch = mocker.patch('cron_jobs.jobs.start_watching', return_value=None)

    jobs.renew_watch(appConfig)

    creds_call.assert_has_calls([mocker.call(my_first_email, appConfig),
                                 mocker.call(my_second_email, appConfig)], any_order=True)
    stop_watch.assert_has_calls([mocker.call(my_creds, my_first_email),
                                 mocker.call(my_creds, my_second_email)], any_order=True)
    start_watch.assert_has_calls([mocker.call(my_creds, my_first_email, appConfig), 
                                  mocker.call(my_creds, my_second_email, appConfig)], any_order=True)

    assert creds_call.call_count == 2
    assert stop_watch.call_count == 2
    assert start_watch.call_count == 2


def test_renew_watch_only_renews_for_active_users(db_conn, mocker, appConfig):
    '''
    Test that only active users' watch calls are updated by renew_watch function
    '''

    my_first_email = 'jschmoe@gmail.com'
    my_first_name = 'Joe Schmoe'
    my_second_email = 'pursufounder@gmail.com'
    my_second_name = 'Pursu Founder'
    my_creds = 'aCredentialsObject'

    uid1 = helper.create_test_user_and_email(
        db_conn=db_conn,
        email=my_first_email,
        name=my_first_name,
        token='aFirstToken')
    _uid2 = helper.create_test_user_and_email(
        db_conn=db_conn,
        email=my_second_email,
        name=my_second_name,
        token='aSecondToken')

    query = "UPDATE users SET active=0 WHERE uid={};".format(uid1)
    helper.execute_test_query(db_conn, query)

    creds_call = mocker.patch('cron_jobs.jobs.get_credentials', return_value=my_creds)
    stop_watch = mocker.patch('cron_jobs.jobs.stop_watching', return_value=None)
    start_watch = mocker.patch('cron_jobs.jobs.start_watching', return_value=None)

    jobs.renew_watch(appConfig)

    creds_call.assert_called_once_with(my_second_email, appConfig)
    stop_watch.assert_called_once_with(my_creds, my_second_email)
    start_watch.assert_called_once_with(my_creds, my_second_email, appConfig)



def test_get_credentials_handles_malformed_user_entries(db_conn, mocker):
    '''
    Test that get_credentials function does not blow up if gmail token does not exist.
    This is a necessary unit test because of errors in sign-up that may result in a user
    having an empty token entry
    '''
    # TODO: Finish
    assert True
