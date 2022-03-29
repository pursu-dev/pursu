import json
import base64
import email_analysis.routes as email_pipeline  # pylint: disable=E0401
from shared import scrape_email  # pylint: disable=E0401
import helper  # pylint: disable=E0401


def test_email_api_health_check(email_api):
    '''
    Test health check route for email analysis api
    '''
    assert email_api.get('/api/email_analysis/health').status_code == 200


def test_get_message_handles_malformed_pubsub_request(email_api):
    '''
    Test get message route for email analysis api when request is malformed
    '''
    data = {
        'message': {}
    }
    my_data = json.dumps(data).encode('utf-8')
    assert email_api.post('/api/email_analysis/new_message', data=my_data).status_code == 200


def test_get_message_handles_lone_history_id_message(email_api, mocker):
    '''
    Test get message route for email analysis api when pub/sub notification only
    has a historyID field. This occurs when we begin watching on a particular
    user email accounts
    '''
    my_data = {
        'message': {
            'data': None
        }
    }
    my_message = {'historyId': 1}

    # Mock encoding and decoding functions so that the message is presented as above
    my_data['message']['data'] = json.dumps(my_message).encode('utf-8')
    mocker.patch('json.loads', side_effect=[my_data, my_message])
    mocker.patch('base64.b64decode', side_effect=iden)
    assert email_api.post('/api/email_analysis/new_message', data=my_data).status_code == 200


def test_get_message_handles_message_when_user_not_in_database(email_api, mocker):
    '''
    Test get message route for email analysis when pub/sub notification is for email
    that doesn't exist in the database. This is exceptional client behavior, but important
    to test for because of our development process
    '''
    my_email = 'jschmoe@gmail.com'
    my_data = {
        'message': {
            'data': None
        }
    }
    my_message = {
        'emailAddress': my_email,
        'historyId': 1
    }

    # Mock encoding and decoding functions so that the message is presented as above
    my_data['message']['data'] = json.dumps(my_message).encode('utf-8')
    mocker.patch('json.loads', side_effect=[my_data, my_message])
    mocker.patch('base64.b64decode', side_effect=iden)
    assert email_api.post('/api/email_analysis/new_message', data=my_data).status_code == 200


def test_get_message_requests_email_using_previous_historyID(email_api, db_conn, mocker):
    '''
    Test that get message route for email analysis queries for the email corresponding to
    a received pub/sub notification, using the previously stored historyID
    '''
    my_mocked_email = {'mock1': 'mock'}
    my_mocked_scraped_email = {'mock2': 'mock'}
    get_email_mock = mocker.patch(
        'email_analysis.routes.get_email',
        return_value=(
            my_mocked_scraped_email,
            my_mocked_email))
    categorize_mock = mocker.patch('email_analysis.routes.categorize_and_update_pipeline')

    my_previous_historyID = '0'
    my_email = 'jschmoe@gmail.com'
    my_data = {
        'message': {
            'data': None
        }
    }
    my_message = {
        'emailAddress': my_email,
        'historyId': '1'
    }
    # Mock encoding and decoding functions so that the message is presented as above
    my_data['message']['data'] = json.dumps(my_message).encode('utf-8')
    mocker.patch('json.loads', side_effect=[my_data, my_message])
    mocker.patch('base64.b64decode', side_effect=iden)

    uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email)

    query = 'UPDATE gmail SET history={} WHERE uid={}'.format(my_previous_historyID, uid)
    helper.execute_test_query(db_conn, query)

    assert email_api.post('/api/email_analysis/new_message', data=my_data).status_code == 200
    get_email_mock.assert_called_once_with(my_email, my_previous_historyID)
    categorize_mock.assert_called_once_with(my_mocked_scraped_email, my_mocked_email, my_email)


def test_get_message_handles_email_grabbing_error(email_api, db_conn, mocker):
    '''
    Test that get message route for email analysis pipeline handles when there is an error in grabbing the email content
    '''
    get_email_mock = mocker.patch('email_analysis.routes.get_email', return_value=(None, None))
    categorize_mock = mocker.patch('email_analysis.routes.categorize_and_update_pipeline')

    my_previous_historyID = '0'
    my_email = 'jschmoe@gmail.com'
    my_data = {
        'message': {
            'data': None
        }
    }
    my_message = {
        'emailAddress': my_email,
        'historyId': '1'
    }
    # Mock encoding and decoding functions so that the message is presented as above
    my_data['message']['data'] = json.dumps(my_message).encode('utf-8')
    mocker.patch('json.loads', side_effect=[my_data, my_message])
    mocker.patch('base64.b64decode', side_effect=iden)

    uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email)

    query = 'UPDATE gmail SET history={} WHERE uid={}'.format(my_previous_historyID, uid)
    helper.execute_test_query(db_conn, query)

    assert email_api.post('/api/email_analysis/new_message', data=my_data).status_code == 200
    get_email_mock.assert_called_once_with(my_email, my_previous_historyID)
    categorize_mock.assert_not_called()


def test_write_email(email_api, db_conn, mocker):
    '''
    Unit test to ensure emails are properly stored when user gives consent
    '''
    mock_anon = mocker.patch('shared.data_utils.anonymize_and_write_to_S3')

    # Need to mock this because we are not making an api request
    mocker.patch('email_analysis.routes.add_to_state')

    my_name = 'Joe Schmoe'
    my_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn, name=my_name, email=my_email)
    query = "UPDATE users SET consent=1 WHERE uid={}".format(uid)
    helper.execute_test_query(db_conn, query)

    email_df = {}
    email_pipeline.write_email(email_df=email_df, user_email=my_email)

    mock_anon.assert_called_once_with(email_df, my_name, my_email)


def test_write_email_does_not_write_email_without_consent(email_api, db_conn, mocker):
    '''
    Unit test to ensure email is only written if user provides explicit data collection consent
    '''
    mock_anon = mocker.patch('shared.data_utils.anonymize_and_write_to_S3')

    my_name = 'Joe Schmoe'
    my_email = 'jschmoe@gmail.com'

    _uid = helper.create_test_user_and_email(db_conn, name=my_name, email=my_email)

    email_df = {}
    email_pipeline.write_email(email_df=email_df, user_email=my_email)
    mock_anon.assert_not_called()


def test_run_models_returns_endpoint_categorization(email_api, db_conn, mocker):
    '''
    Unit test to ensure that the categorization returned by ML endpoints is correctly returned
    '''
    class myObj:
        def read(self):
            return 0

    my_return_value = {'Body': myObj()}
    mock_endpoint = mocker.patch(
        'email_analysis.sagemaker_client.invoke_endpoint',
        return_value=my_return_value)

    email_df = {
        'subject': 'hello',
        'body': 'goodbye'
    }
    out = email_pipeline.run_models(scraped_email=email_df)

    assert mock_endpoint.call_count == 2
    assert out == 0


def test_run_models_does_not_run_categorization_for_irrelevant_email(email_api, db_conn, mocker):
    '''
    Unit test to ensure that categorization model is not invoked if email is irrelevant
    '''
    class myObj:
        def read(self):
            return 1

    my_return_value = {'Body': myObj()}
    mock_endpoint = mocker.patch(
        'email_analysis.sagemaker_client.invoke_endpoint',
        return_value=my_return_value)

    email_df = {
        'subject': 'hello',
        'body': 'goodbye'
    }

    out = email_pipeline.run_models(scraped_email=email_df)

    assert mock_endpoint.call_count == 1
    assert out == -1


def test_categorize_and_update_pipeline_ignores_irrelevant_emails(email_api, db_conn, mocker):
    '''
    Unit test to ensure that irrelevant job updates, eg (LinkedIn updates) are not pushed through pipeline
    '''
    denylist_filter = mocker.patch('shared.filters.denylist_filter', return_value=False)
    model_func = mocker.patch('email_analysis.routes.run_models', return_value=None)
    email_parse_func = mocker.patch(
        'email_analysis.parse_info.get_email_information',
        return_value=None)
    update_pipeline_func = mocker.patch(
        'email_analysis.pipeline_logic.update_pipeline',
        return_value=None)
    write_email_func = mocker.patch('email_analysis.routes.write_email', return_value=None)

    my_email = 'jschmoe@gmail.com'
    my_email_resp = {'random_field': 'hello'}
    my_email_df = {'body': 'hello'}

    email_pipeline.categorize_and_update_pipeline(
        email_df=my_email_df,
        raw_email_resp=my_email_resp,
        user_email=my_email)

    denylist_filter.assert_called()
    model_func.assert_not_called()
    email_parse_func.assert_not_called()
    update_pipeline_func.assert_not_called()
    write_email_func.assert_not_called()


def iden(x):
    '''
    Helper function to use in mocking
    '''
    return x
