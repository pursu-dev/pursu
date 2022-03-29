''' Unit tests for google credentials logic '''

from shared import config  # pylint: disable=E0401
import helper  # pylint: disable=E0401

def test_get_google_project_credentials_for_email_basic(db_conn, appConfig):
    '''
    Basic functionality testing for getting correct project credentials
    '''
    helper.create_test_user_and_email(db_conn, email='jschmoe@gmail.com')
    google_creds = config.get_google_project_credentials_for_email(appConfig, 'jschmoe@gmail.com')
    assert google_creds.client_id == appConfig.GOOGLE_CREDENTIALS[1]['CLIENT_ID']
    assert google_creds.client_secret == appConfig.GOOGLE_CREDENTIALS[1]['CLIENT_SECRET']
    assert google_creds

# def test_get_next_available_project_selects_project_with_space(db_conn, appConfig):
#     '''
#     Check if project credentials query selects empty project for non-associated email
#     '''
#     target_gcid = helper.create_test_google_project(db_conn, 
#                                                     appConfig, 
#                                                     client_id='test_id2', 
#                                                     client_secret='test_secret2', 
#                                                     project_id='pid', 
#                                                     topic='topic')

#     # Now there are two google projects (default created on test startup)

#     # Mark original project as full
#     helper.execute_test_query(db_conn, "UPDATE google_projects SET has_space=0 WHERE gcid=1;")

#     google_creds = config.get_google_project_credentials_for_email(appConfig, 'jschmoe@gmail.com')

#     assert google_creds.client_id == appConfig.GOOGLE_CREDENTIALS[target_gcid]['CLIENT_ID']
#     assert google_creds.client_secret == appConfig.GOOGLE_CREDENTIALS[target_gcid]['CLIENT_SECRET']
#     assert google_creds.project_id == 'pid'
#     assert google_creds.topic == 'topic'
#     assert google_creds.has_space

def test_get_google_project_credentials_for_client_id(db_conn, appConfig):
    '''
    Check that correct project credentials are returned for a specific client id
    '''
    target_gcid = helper.create_test_google_project(db_conn, 
                                                    appConfig, 
                                                    client_id='test_id2', 
                                                    client_secret='test_secret2', 
                                                    project_id='pid', 
                                                    topic='topic')

    # Now there are two google projects (default created on test startup)
    google_creds = config.get_google_project_credentials_for_client_id(appConfig, 'test_id2')
    assert google_creds.client_id == appConfig.GOOGLE_CREDENTIALS[target_gcid]['CLIENT_ID']
    assert google_creds.client_secret == appConfig.GOOGLE_CREDENTIALS[target_gcid]['CLIENT_SECRET']