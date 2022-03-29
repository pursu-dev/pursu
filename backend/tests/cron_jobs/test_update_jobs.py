''' Unit tests for various functions in module update_jobs '''

import helper  # pylint: disable=E0401
from cron_jobs import update_jobs  # pylint: disable=E0401


def test_update_jobs(mocker, db_conn, appConfig):
    '''
    Naive test for company matching
    '''
    google_cid = helper.create_test_company(db_conn, name='Google')
    helper.create_test_company(db_conn, name='Facebook')
    helper.create_test_company(db_conn, name='Salesforce')

    is_internship = True
    jobs_lists = [['http://google.com', is_internship]]
    mock_update_jobs_functions(mocker, jobs_lists)

    company_name = 'Google'
    link = 'google.com'
    location = 'Mountain View'
    notes = 'Here are my notes'
    parsed_list = [[company_name, link, location, notes]]

    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=parsed_list)

    job_listing_update_manager = update_jobs.JobListingUpdateManager(appConfig)
    job_listing_update_manager.update_jobs()

    query = "SELECT name, cid FROM jobs;"
    res = helper.execute_test_query(db_conn, query)[0]

    assert set(res) == set([company_name, google_cid])


def test_update_jobs_new_info(mocker, db_conn, appConfig):
    '''
    Test that newly parsed info will correctly update jobs table
    '''
    google_cid = helper.create_test_company(db_conn, name='Google')
    helper.create_test_company(db_conn, name='Facebook')
    helper.create_test_company(db_conn, name='Salesforce')

    is_internship = True
    jobs_lists = [['http://google.com', is_internship]]
    mock_update_jobs_functions(mocker, jobs_lists)

    company_name = 'Google'
    link = 'google.com'
    location = 'Mountain View'
    notes = 'Here are my notes'
    parsed_list = [[company_name, None, None, None]]
    updated_list = [[company_name, link, location, notes]]

    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=parsed_list)
    job_listing_update_manager = update_jobs.JobListingUpdateManager(appConfig)
    job_listing_update_manager.update_jobs()

    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=updated_list)
    job_listing_update_manager.update_jobs()

    query = "SELECT name, cid, link, location, notes FROM jobs;"
    res = helper.execute_test_query(db_conn, query)[0]

    assert set(res) == set([company_name, google_cid, link, location, notes])


def test_update_jobs_parsed_list_empty(mocker, db_conn, appConfig):
    '''
    Sanity check test to ensure that empty list adds nothing to jobs table
    '''
    google_cid = helper.create_test_company(db_conn, name='Google')
    helper.create_test_company(db_conn, name='Facebook')
    helper.create_test_company(db_conn, name='Salesforce')

    is_internship = True
    jobs_lists = [['http://google.com', is_internship]]
    mock_update_jobs_functions(mocker, jobs_lists)

    company_name = 'Google'
    link = 'google.com'
    location = 'Mountain View'
    notes = 'Here are my notes'
    parsed_list = [[company_name, link, location, notes]]
    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=parsed_list)
    job_listing_update_manager = update_jobs.JobListingUpdateManager(appConfig)
    job_listing_update_manager.update_jobs()

    updated_list = []
    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=updated_list)
    job_listing_update_manager.update_jobs()

    query = "SELECT name, cid, link, location, notes FROM jobs;"
    res = helper.execute_test_query(db_conn, query)[0]

    assert set(res) == set([company_name, google_cid, link, location, notes])


def test_update_jobs_remove_info(mocker, db_conn, appConfig):
    '''
    Test that newly parsed info that indicates job posting closing will remove previous entry from jobs table
    '''
    google_cid = helper.create_test_company(db_conn, name='Google')
    helper.create_test_company(db_conn, name='Facebook')
    helper.create_test_company(db_conn, name='Salesforce')

    is_internship = True
    jobs_lists = [['http://google.com', is_internship]]
    mock_update_jobs_functions(mocker, jobs_lists)

    company_name = 'Google'
    link = 'google.com'
    location = 'Mountain View'
    notes = 'Here are my notes'
    parsed_list = [[company_name, link, location, notes]]
    updated_list = [[company_name, None, None, None]]

    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=parsed_list)
    job_listing_update_manager = update_jobs.JobListingUpdateManager(appConfig)
    job_listing_update_manager.update_jobs()

    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=updated_list)
    job_listing_update_manager.update_jobs()

    query = "SELECT name, cid, link, location, notes FROM jobs;"
    res = helper.execute_test_query(db_conn, query)

    assert set(res) == set()


def test_update_jobs_add_info_no_link(mocker, db_conn, appConfig):
    '''
    Test that newly parsed info that indicates job posting closing won't be inserted into jobs table
    '''
    google_cid = helper.create_test_company(db_conn, name='Google')
    helper.create_test_company(db_conn, name='Facebook')
    helper.create_test_company(db_conn, name='Salesforce')

    is_internship = True
    jobs_lists = [['http://google.com', is_internship]]
    mock_update_jobs_functions(mocker, jobs_lists)

    company_name = 'Google'
    link = None
    location = 'Mountain View'
    notes = 'Here are my notes'
    parsed_list = [[company_name, link, location, notes]]

    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=parsed_list)
    job_listing_update_manager = update_jobs.JobListingUpdateManager(appConfig)
    job_listing_update_manager.update_jobs()

    query = "SELECT name, cid, link, location, notes FROM jobs;"
    res = helper.execute_test_query(db_conn, query)

    assert set(res) == set()


def test_update_jobs_multiple_companies(mocker, db_conn, appConfig):
    '''
    Naive test that multiple companies are added correctly to the jobs table
    '''
    google_cid = helper.create_test_company(db_conn, name='Google')
    fb_cid = helper.create_test_company(db_conn, name='Facebook')
    salesforce_cid = helper.create_test_company(db_conn, name='Salesforce')

    is_internship = True
    jobs_lists = [['http://google.com', is_internship]]
    mock_update_jobs_functions(mocker, jobs_lists)

    companies_info = {
        'Google': {'link': 'google.com',
                   'location': 'Mountain View',
                   'notes': 'app open'},
        'Facebook': {'link': 'facebook.com',
                     'location': 'Menlo Park',
                     'notes': 'hype af'},
        'Salesforce': {'link': None,
                       'location': 'San Francisco',
                       'notes': 'tower'},
    }

    parsed_list = [['Google', companies_info['Google']['link'], companies_info['Google']['location'], companies_info['Google']['notes']],
                   ['Facebook',
                    companies_info['Facebook']['link'],
                    companies_info['Facebook']['location'],
                    companies_info['Facebook']['notes']],
                   ['Salesforce', companies_info['Salesforce']['link'], companies_info['Salesforce']['location'], companies_info['Salesforce']['notes']]]

    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=parsed_list)
    job_listing_update_manager = update_jobs.JobListingUpdateManager(appConfig)
    job_listing_update_manager.update_jobs()

    query = "SELECT name, cid, link, location, notes FROM jobs;"
    res = helper.execute_test_query(db_conn, query)

    assert set(res) == set([('Facebook', fb_cid, companies_info['Facebook']['link'], companies_info['Facebook']['location'], companies_info['Facebook']['notes']),
                            ('Google',
                             google_cid,
                             companies_info['Google']['link'],
                             companies_info['Google']['location'],
                             companies_info['Google']['notes'])
                            ])


def test_update_jobs_set_difference(mocker, db_conn, appConfig):
    '''
    Tests that multiple companies are added correctly to the jobs table
    '''
    google_cid = helper.create_test_company(db_conn, name='Google')
    fb_cid = helper.create_test_company(db_conn, name='Facebook')
    salesforce_cid = helper.create_test_company(db_conn, name='Salesforce')

    is_internship = True
    jobs_lists = [['http://google.com', is_internship]]
    mock_update_jobs_functions(mocker, jobs_lists)

    companies_info = {
        'Google': {'link': 'google.com',
                   'location': 'Mountain View',
                   'notes': 'app open'},
        'Facebook': {'link': 'facebook.com',
                     'location': 'Menlo Park',
                     'notes': 'hype af'},
        'Salesforce': {'link': None,
                       'location': 'San Francisco',
                       'notes': ' tower'},
    }

    updated_companies_info = {
        'Google': {'link': None,
                   'location': 'Mountain View',
                   'notes': 'app closed'},
        'Facebook': {'link': 'facebook.com',
                     'location': 'New York City',
                     'notes': 'super hype af'},
        'Salesforce': {'link': 'salesforce.com',
                       'location': 'San Francisco',
                       'notes': ' tower'},
    }

    parsed_list = [['Google', companies_info['Google']['link'], companies_info['Google']['location'], companies_info['Google']['notes']],
                   ['Facebook',
                    companies_info['Facebook']['link'],
                    companies_info['Facebook']['location'],
                    companies_info['Facebook']['notes']],
                   ['Salesforce', companies_info['Salesforce']['link'], companies_info['Salesforce']['location'], companies_info['Salesforce']['notes']]]

    updated_list = [['Google', updated_companies_info['Google']['link'], updated_companies_info['Google']['location'], updated_companies_info['Google']['notes']],
                    ['Facebook',
                     updated_companies_info['Facebook']['link'],
                     updated_companies_info['Facebook']['location'],
                     updated_companies_info['Facebook']['notes']],
                    ['Salesforce', updated_companies_info['Salesforce']['link'], updated_companies_info['Salesforce']['location'], updated_companies_info['Salesforce']['notes']]]

    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=parsed_list)
    job_listing_update_manager = update_jobs.JobListingUpdateManager(appConfig)
    job_listing_update_manager.update_jobs()

    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=updated_list)
    job_listing_update_manager.update_jobs()

    query = "SELECT name, cid, link, location, notes FROM jobs;"
    res = helper.execute_test_query(db_conn, query)

    assert set(res) == set([('Salesforce',
                             salesforce_cid,
                             updated_companies_info['Salesforce']['link'],
                             updated_companies_info['Salesforce']['location'],
                             updated_companies_info['Salesforce']['notes']),
                            ('Facebook',
                             fb_cid,
                             updated_companies_info['Facebook']['link'],
                             updated_companies_info['Facebook']['location'],
                             updated_companies_info['Facebook']['notes'])
                            ])


def test_update_jobs_internship_and_fulltime(mocker, db_conn, appConfig):
    '''
    Tests that internship and full time insertions will create distinct rows
    '''
    google_cid = helper.create_test_company(db_conn, name='Google')

    internship_lists = [['http://google.com', True]]
    mock_update_jobs_functions(mocker, internship_lists)

    company_name = 'Google'
    link = 'google.com'
    location = 'Mountain View'
    internship_notes = 'Here are my notes about the internship'
    fulltime_notes = 'Here are my notes about the full time'
    internship_parsed_list = [[company_name, link, location, internship_notes]]
    fulltime_parsed_list = [[company_name, link, location, fulltime_notes]]

    list_md_supplier_internship = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=internship_parsed_list)
    job_listing_update_manager = update_jobs.JobListingUpdateManager(appConfig)
    job_listing_update_manager.update_jobs()

    jobs_lists = [['http://google.com', False]]
    mock_update_jobs_functions(mocker, jobs_lists)

    list_md_supplier_fulltime = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=fulltime_parsed_list)
    job_listing_update_manager.update_jobs()

    query = "SELECT name, cid, notes, internship FROM jobs;"
    res = helper.execute_test_query(db_conn, query)

    assert set(res) == set([(company_name, google_cid, internship_notes, True), (
        company_name, google_cid, fulltime_notes, False)])


def test_update_jobs_similar_name(mocker, db_conn, appConfig):
    google_cid = helper.create_test_company(db_conn, name='Google', domain='google')

    is_internship = True
    jobs_lists = [['http://google.com', is_internship]]
    mock_update_jobs_functions(mocker, jobs_lists)

    new_company_info = {
        'Goggle': {'link': 'google.com',
                   'location': 'Mountain View',
                   'notes': 'app open'},
    }

    parsed_list = [['Goggle',
                    new_company_info['Goggle']['link'],
                    new_company_info['Goggle']['location'],
                    new_company_info['Goggle']['notes']]]

    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=parsed_list)
    job_listing_update_manager = update_jobs.JobListingUpdateManager(appConfig)
    job_listing_update_manager.update_jobs()

    query = "SELECT name, cid, link, location, notes FROM jobs;"
    res = helper.execute_test_query(db_conn, query)

    assert set(res) == set([('Goggle',
                             google_cid,
                             new_company_info['Goggle']['link'],
                             new_company_info['Goggle']['location'],
                             new_company_info['Goggle']['notes'])
                            ])


def mock_update_jobs_functions(mocker, jobs_lists):
    mocker.patch('cron_jobs.update_jobs.generate_jobs_lists', return_value=jobs_lists)
    mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_markdown_file',
        return_value=None)

def test_update_jobs_null_domain(mocker, db_conn, appConfig):
    '''
    Test to make sure that company with null domain and invalid name doesn't get matched 
    '''
    google_cid = helper.create_test_company(db_conn, name='Google')

    is_internship = True
    jobs_lists = [['http://google.com', is_internship]]
    mock_update_jobs_functions(mocker, jobs_lists)

    company_name = 'Gogle'
    link = 'google.com'
    location = 'Mountain View'
    notes = 'Here are my notes'
    parsed_list = [[company_name, link, location, notes]]

    list_md_supplier = mocker.patch(
        'cron_jobs.update_jobs.JobListingUpdateManager.parse_list',
        return_value=parsed_list)

    job_listing_update_manager = update_jobs.JobListingUpdateManager(appConfig)
    job_listing_update_manager.update_jobs()

    query = "SELECT name, cid, approved FROM jobs;"
    res = helper.execute_test_query(db_conn, query)[0]

    assert set(res) == set([company_name, None, False])
