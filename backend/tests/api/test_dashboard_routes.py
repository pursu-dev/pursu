import pytest
import json
import datetime
from email_analysis import LABELS_TO_CATEGORIES, CATEGORIES_TO_LABELS  # pylint: disable=E0401
import api.dashboard_routes as main_pipeline  # pylint: disable=E0401
import helper  # pylint: disable=E0401


def test_api_edit_dashboard(main_api, db_conn):
    '''
    Test route to edit pipelines in user dashboard
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, email='jschmoe@gmail.com')
    cid = helper.create_test_company(db_conn=db_conn)
    pid = helper.create_test_pipeline(db_conn=db_conn, uid=uid, cid=cid)

    data = {
        'token': 'token',
        'company': 'Google',
        'deadline': None,
        'notes': 'Testing notes',
        'pid': pid,
        'stage': CATEGORIES_TO_LABELS['OFFER']
    }
    status = main_api.post('/api/dashboard/edit', json=data).status_code

    query = "SELECT stage, notes FROM pipelines WHERE pid={};".format(pid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert status == 200
    assert list(db_res) == [CATEGORIES_TO_LABELS['OFFER'], 'Testing notes']


def test_api_edit_dashboard_manual_entry(main_api, db_conn):
    '''
    Test route to edit pipelines with manually entered company in user dashboard
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, email='jschmoe@gmail.com')
    cid = helper.create_test_company(db_conn=db_conn)
    pid = helper.create_test_pipeline(db_conn=db_conn, uid=uid, cid=cid)

    user_gen_company = 'Facebook'
    data = {
        'token': 'token',
        'company': user_gen_company,
        'pid': pid
    }
    status = main_api.post('/api/dashboard/edit', json=data).status_code
    query1 = "SELECT cid FROM pipelines WHERE pid={};".format(pid)
    db_res_1 = helper.execute_test_query(db_conn, query1)[0]

    cid = db_res_1[0]
    query2 = "SELECT name, user_created FROM companies WHERE cid={};".format(cid)
    db_res_2 = helper.execute_test_query(db_conn, query2)[0]

    assert status == 201
    assert list(db_res_1) == [cid]
    assert list(db_res_2) == [user_gen_company, 1]


def test_api_edit_dashboard_selects_correct_pipeline(main_api, db_conn):
    '''
    Test route to edit pipelines when there exists more than one pipeline
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, email='jschmoe@gmail.com')
    cid_1 = helper.create_test_company(db_conn=db_conn)
    cid_2 = helper.create_test_company(db_conn=db_conn, name='Facebook')
    pid_1 = helper.create_test_pipeline(
        db_conn=db_conn,
        uid=uid,
        cid=cid_1,
        stage=CATEGORIES_TO_LABELS['INTERVIEW'])
    pid_2 = helper.create_test_pipeline(
        db_conn=db_conn,
        uid=uid,
        cid=cid_2,
        stage=CATEGORIES_TO_LABELS['INTERVIEW'])

    data = {
        'token': 'token',
        'company': 'Google',
        'deadline': None,
        'notes': 'Testing notes',
        'pid': pid_1,
        'stage': CATEGORIES_TO_LABELS['OFFER']
    }

    status = main_api.post('/api/dashboard/edit', json=data).status_code
    query = "SELECT pid, stage FROM pipelines WHERE stage=5;"
    db_res_1 = helper.execute_test_query(db_conn, query)[0]

    query = "SELECT pid, stage FROM pipelines WHERE pid={}".format(pid_2)
    db_res_2 = helper.execute_test_query(db_conn, query)[0]

    assert status == 200
    assert list(db_res_1) == [pid_1, CATEGORIES_TO_LABELS['OFFER']]
    assert list(db_res_2) == [pid_2, CATEGORIES_TO_LABELS['INTERVIEW']]


def test_api_delete_from_dashboard(main_api, db_conn):
    '''
    Test route to delete a pipeline from user dashboard
    '''
    myEmail = 'jschmoe@gmail.com'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=myEmail)
    cid = helper.create_test_company(db_conn=db_conn)
    pid = helper.create_test_pipeline(db_conn=db_conn, uid=uid, cid=cid)

    data = {
        'token': 'token',
        'pid': pid
    }

    status = main_api.post('/api/dashboard/delete', json=data).status_code

    query = "SELECT * FROM pipelines WHERE pid={};".format(pid)
    db_res = helper.execute_test_query(db_conn, query)

    assert status == 200
    assert db_res == []


def test_api_add_pipeline(main_api, db_conn, mocker):
    '''
    Test route to add pipeline to user dashboard
    '''
    filter_thread = mocker.patch('threading.Thread.start', return_value=None)

    myEmail = 'jschmoe@gmail.com'
    myStage = CATEGORIES_TO_LABELS['INTERVIEW']
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=myEmail)
    cid = helper.create_test_company(db_conn=db_conn)

    data = {
        'token': 'token',
        'uid': uid,
        'stage': myStage,
        'company_name': 'Google',
    }

    status = main_api.post('/api/dashboard/add', json=data).status_code

    query = "SELECT stage FROM pipelines WHERE uid={} AND cid={};"\
        .format(uid, cid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    filter_thread.assert_called_once()
    assert status == 200
    assert list(db_res) == [CATEGORIES_TO_LABELS['INTERVIEW']]


def test_api_add_pipeline_with_notes(main_api, db_conn, mocker):
    '''
    Test route to add pipeline to user dashboard
    '''
    filter_thread = mocker.patch('threading.Thread.start', return_value=None)

    myEmail = 'jschmoe@gmail.com'
    myStage = CATEGORIES_TO_LABELS['INTERVIEW']
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=myEmail)
    cid = helper.create_test_company(db_conn=db_conn)

    data = {
        'token': 'token',
        'uid': uid,
        'stage': myStage,
        'company_name': 'Google',
        'notes': 'I love Google!'
    }

    status = main_api.post('/api/dashboard/add', json=data).status_code

    query = "SELECT stage, notes FROM pipelines WHERE uid={} AND cid={};"\
        .format(uid, cid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    filter_thread.assert_called_once()
    assert status == 200
    assert list(db_res) == [CATEGORIES_TO_LABELS['INTERVIEW'], data["notes"]]


def test_api_add_manual_entry_pipeline(main_api, db_conn, mocker):
    '''
    Test route to add user-created company pipeline to user dashboard
    '''
    filter_thread = mocker.patch('threading.Thread.start', return_value=None)

    myEmail = 'jschmoe@gmail.com'
    myStage = CATEGORIES_TO_LABELS['INTERVIEW']
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=myEmail)

    data = {
        'token': 'token',
        'uid': uid,
        'stage': myStage,
        'company_name': 'Google',
    }

    status = main_api.post('/api/dashboard/add', json=data).status_code
    query1 = "SELECT stage, cid FROM pipelines WHERE uid={}".format(uid)
    db_res = helper.execute_test_query(db_conn, query1)[0]

    cid = db_res[1]
    query2 = "SELECT name, user_created FROM companies WHERE cid={}".format(cid)
    db_res_2 = helper.execute_test_query(db_conn, query2)[0]

    filter_thread.assert_not_called()
    assert status == 201
    assert list(db_res) == [CATEGORIES_TO_LABELS['INTERVIEW'], cid]
    assert list(db_res_2) == ['Google', 1]


def test_api_deactivate_pipeline(main_api, db_conn):
    '''
    Test route to activate a pipeline in user dashboard
    '''
    myEmail = 'jschmoe@gmail.com'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=myEmail)
    cid = helper.create_test_company(db_conn=db_conn)
    pid = helper.create_test_pipeline(db_conn=db_conn, uid=uid, cid=cid)

    data = {
        'email': myEmail,
        'pid': pid
    }

    status = main_api.post('/api/dashboard/deactivate', json=data).status_code

    query = "SELECT active FROM pipelines WHERE pid={};".format(pid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert status == 200
    assert list(db_res) == [False]


def test_enter_new_company(main_api, db_conn):
    '''
    Unit test for enter_new_company.
    Ensures company inserted, and filter version number incremented
    '''
    query = "INSERT INTO filters(name, query, version)\
         VALUES('filt0', 'query', 0);"
    helper.execute_test_query(db_conn, query)
    company_name = 'Google'
    cid = main_pipeline.enter_new_company(company_name=company_name, user_created=False)

    query = "SELECT name, filt_version FROM companies WHERE cid={};".format(cid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert db_res == (company_name, 1)


def test_user_requires_filter_update(main_api, db_conn):
    '''
    Unit test for user_requires_filter_update
    '''
    my_email = 'jschmoe@gmail.com'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email)
    first_cid = helper.create_test_company(db_conn=db_conn, name='Google', filt_version=1)
    second_cid = helper.create_test_company(db_conn=db_conn, name='Facebook', filt_version=2)

    query = "UPDATE users SET filt_version=1 WHERE uid={}".format(uid)
    helper.execute_test_query(db_conn, query)

    assert main_pipeline.user_requires_filter_update(uid, first_cid) == False
    assert main_pipeline.user_requires_filter_update(uid, second_cid) == True


def test_pipeline_constraints(main_api, db_conn):
    '''
    Unit test to ensure that operations to dashboard check validity of request
    '''
    myEmail = 'jschmoe@gmail.com'
    uid = helper.create_test_user_and_email(db_conn=db_conn)
    cid = helper.create_test_company(db_conn=db_conn)
    pid = helper.create_test_pipeline(db_conn, uid, cid)

    data = {
        'email': myEmail,
        'pid': pid + 1,
        'token': 'token'
    }

    status = main_api.post('/api/dashboard/delete', json=data).status_code

    assert status == 400
