import data_ingestion.routes as data_pipeline # pylint: disable=E0401
import helper  # pylint: disable=E0401


class MockCreds:
    def __init__(self, my_email):
        self.id_token = {'email': my_email}


def test_data_api_health_check(data_api):
    '''
    Test health check route for data ingestion api
    '''
    assert data_api.get('/api/data_ingestion/health').status_code == 200


def test_data_api_training_data_collection_rejects_requests_without_encoding(data_api):
    '''
    Test that main api route for data ingestion api returns forbidden error for unsafe requests
    '''
    data = {
        'token': 'myToken'
    }

    # Headers should have X-Requested-with
    headers = {}
    assert data_api.post(
        '/api/data_ingestion/storeauthtraining',
        json=data,
        headers=headers).status_code == 403


def test_data_api_training_data_collection_ensures_no_repeat_providers(data_api, mocker, db_conn):
    '''
    Check that main api route for data ingestion api checks that user has not previously provided data
    '''
    my_name = 'Joe Schmoe'
    my_email = 'jschmoe@gmail.com'

    my_creds = MockCreds(my_email)
    data_pipeline.appConfig.GOOGLE_CLIENT_CREDENTIALS = {
        'client_id': 'client_id',
        'client_secret': 'client_secret'
    }
    
    data = {'token': 'myToken'}
    headers = {'X-Requested-With': 'myHeader'}
    _uid = helper.create_test_user_and_email(db_conn, name=my_name, email=my_email)

    query = "INSERT INTO data_providers(email) VALUES('{}');".format(my_email)
    helper.execute_test_query(db_conn, query)

    data_grab_thread = mocker.patch('threading.Thread', return_value=None)
    mocker.patch(
        'oauth2client.client.credentials_from_code',
        return_value=my_creds)

    assert data_api.post(
        '/api/data_ingestion/storeauthtraining',
        json=data,
        headers=headers).status_code == 200
    assert data_grab_thread.not_called()


def test_data_api_training_data_collection_executes_search_for_user(data_api, mocker, db_conn):
    '''
    Test that main api route for data ingestion api properly spins up a new thread to gather user data
    '''
    my_name = 'Joe Schmoe'
    my_email = 'jschmoe@gmail.com'

    my_creds = MockCreds(my_email)
    data_pipeline.appConfig.GOOGLE_CLIENT_CREDENTIALS = {
        'client_id': 'client_id',
        'client_secret': 'client_secret'
    }

    data = {'token': 'myToken'}
    headers = {'X-Requested-With': 'myHeader'}
    _uid = helper.create_test_user_and_email(db_conn, name=my_name, email=my_email)

    data_grab_thread = mocker.patch('data_ingestion.routes.gather_training_data', return_value=None)
    mocker.patch(
        'oauth2client.client.credentials_from_code',
        return_value=my_creds)

    assert data_api.post(
        '/api/data_ingestion/storeauthtraining',
        json=data,
        headers=headers).status_code == 200
    assert data_grab_thread.called_once_with(
        target=data_pipeline.gather_training_data, args=[
            my_email, my_creds])


def test_data_api_renew_watch(data_api, mocker, db_conn):
    '''
    Test that renew watch api route correctly invokes cron job functions
    '''
    mocker.patch('data_ingestion.routes.stop_inactive_and_renew', return_value=None)
    status = data_api.get('/api/data_ingestion/watch_cron_job').status_code
    assert status == 200
