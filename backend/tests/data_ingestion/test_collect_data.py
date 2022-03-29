from data_ingestion import collect_data # pylint: disable=E0401

def test_gather_training_data(db_conn, mocker):
    '''
    Test function to gather training data for a user. Ensure that 
    all queries are searched for given user email
    '''
    my_queries = ['query1', 'query2', 'query3']
    my_name = 'Joe Schmoe'
    my_email = 'jschmoe@gmail.com'

    creds = mocker.MagicMock()
    gmail_instance = mocker.MagicMock()
    creds.authorize.return_value = None
    creds.id_token.return_value = {'name': my_name}
    mocker.patch('apiclient.discovery.build', return_value=gmail_instance)
    filt_request = mocker.patch('shared.filters.get_filters', return_value=my_queries)
    exec_search = mocker.patch('data_ingestion.collect_data.execute_search', return_value=None)

    collect_data.gather_training_data(my_email, creds)
    expected_calls = [mocker.call('query1', gmail_instance, my_name, my_email), 
                      mocker.call('query2', gmail_instance, my_name, my_email), 
                      mocker.call('query3', gmail_instance, my_name, my_email)]

    assert filt_request.call_count == 1
    assert exec_search.has_calls(expected_calls)

def test_execute_search_writes_all_valid_emails_in_single_page(db_conn, mocker):
    '''
    Test function to execute search on user account for single page of query answer
    '''
    gmail_service = mocker.MagicMock()

    sample_message = {'subject': 'A Subject', 'body': 'A Body'}

    my_messages_return_value = {'messages': [{'id': 10}, {'id': 20}]}
    gmail_service.users().messages().list().execute.return_value = my_messages_return_value
    gmail_service.users().messages().get().execute.return_value = sample_message

    scrape_email = mocker.patch('shared.scrape_email.scrape_email_info', return_value=sample_message)
    blist_filter = mocker.patch('shared.filters.denylist_filter', return_value=True)
    anonymize_call = mocker.patch('shared.data_utils.anonymize_email', return_value=sample_message)
    _pandas_dataframe = mocker.patch('pandas.DataFrame', return_value=[sample_message])
    s3_write = mocker.patch('shared.data_utils.write_to_s3', return_value=None)
    
    collect_data.execute_search('the query', gmail_service, 'Joe Schmoe', 'jschmoe@gmail.com')

    assert scrape_email.called_with(sample_message)
    assert blist_filter.called_with(sample_message)
    assert anonymize_call.called_with(sample_message)
    assert s3_write.called_with([sample_message])

def test_execute_search_does_not_write_denylisted_emails(db_conn, mocker):
    '''
    Ensure that execute search function only writes email that would pass through layer2 filter
    '''
    gmail_service = mocker.MagicMock()

    sample_message = {'subject': 'A Subject', 'body': 'A Body'}

    my_messages_return_value = {'messages': [{'id': 10}, {'id': 20}]}
    gmail_service.users().messages().list().execute.return_value = my_messages_return_value
    gmail_service.users().messages().get().execute.return_value = sample_message

    _scrape_email = mocker.patch('shared.scrape_email.scrape_email_info', return_value=sample_message)
    _blist_filter = mocker.patch('shared.filters.denylist_filter', return_value=False)
    anonymize_call = mocker.patch('shared.data_utils.anonymize_email', return_value=sample_message)
    _pandas_dataframe = mocker.patch('pandas.DataFrame', return_value=[sample_message])
    s3_write = mocker.patch('shared.data_utils.write_to_s3', return_value=None)

    collect_data.execute_search('the query', gmail_service, 'Joe Schmoe', 'jschmoe@gmail.com')

    assert anonymize_call.not_called()
    assert s3_write.not_called()

def test_execute_search_traverses_through_all_pages_of_response(db_conn, mocker):
    '''
    Check that execute search function checks entire API response
    '''
    gmail_service = mocker.MagicMock()

    my_first_response = {'messages': [{'id': 10}, {'id': 20}], 'nextPageToken': 1}
    my_second_response = {'messages': [{'id': 30}, {'id': 40}]}
    sample_message = {'subject': 'A Subject', 'body': 'A Body'}

    gmail_service.users().messages().list().execute.side_effect = [my_first_response, my_second_response]
    gmail_service.users().messages().get().execute.return_value = sample_message

    scrape_email = mocker.patch('shared.scrape_email.scrape_email_info', return_value=sample_message)
    _blist_filter = mocker.patch('shared.filters.denylist_filter', return_value=True)
    _anonymize_call = mocker.patch('shared.data_utils.anonymize_email')
    _pandas_dataframe = mocker.patch('pandas.DataFrame')
    s3_write = mocker.patch('shared.data_utils.write_to_s3', return_value=None)

    collect_data.execute_search('the query', gmail_service, 'Joe Schmoe', 'jschmoe@gmail.com')

    expected_scrape_calls = [mocker.call({'id': 10}), mocker.call({'id': 20}), mocker.call({'id': 30}), mocker.call({'id': 40})]

    assert s3_write.call_count == 2
    assert scrape_email.has_calls(expected_scrape_calls)
    assert scrape_email.call_count == 4