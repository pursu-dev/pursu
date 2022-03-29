import pytest
import json
import datetime
import api.queries_routes as main_pipeline  # pylint: disable=E0401
import helper  # pylint: disable=E0401


def test_companies_query(main_api, db_conn):
    '''
    Test queries route that grabs all companies
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, email='jschmoe@gmail.com')
    cid = helper.create_test_company(db_conn=db_conn)
    pid = helper.create_test_pipeline(db_conn=db_conn, uid=uid, cid=cid)

    data = {
        'query_name': 'companies',
        'token': 'token'
    }

    response = main_api.post('/api/queries', json=data)

    data, status = json.loads(response.data), response.status_code

    assert status == 200
    assert data == [[cid, 'Google', None]]


def test_companies_query_multiple(main_api, db_conn):
    '''
    Test queries route that grabs all companies
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, email='jschmoe@gmail.com')
    cid_google = helper.create_test_company(db_conn=db_conn)
    cid_fb = helper.create_test_company(db_conn=db_conn, name='Facebook')
    pid = helper.create_test_pipeline(db_conn=db_conn, uid=uid, cid=cid_google)

    data = {
        'query_name': 'companies',
        'token': 'token'
    }

    response = main_api.post('/api/queries', json=data)

    data, status = json.loads(response.data), response.status_code

    assert status == 200
    assert data == [[cid_fb, 'Facebook', None], [cid_google, 'Google', None]]


def test_user_info_query(main_api, db_conn):
    '''
    Test queries route that grabs user info for given token
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, name='Joe Schmoe', email='jschmoe@gmail.com', token='token')
    uid_fake = helper.create_test_user_and_email(db_conn=db_conn, name='Jane Doe', email='fake@gmail.com', token='fake_token')
    rid = helper.create_test_referral_entry(db_conn=db_conn, uid=uid, points=5, redemptions=0)

    data = {
        'query_name': 'user_info',
        'token': 'token'
    }

    response = main_api.post('/api/queries', json=data)

    data, status = json.loads(response.data), response.status_code

    assert status == 200
    assert data == [[uid, 'Joe Schmoe', 'University of Michigan', 'Computer Science', 2023, None, None, 'jschmoe@gmail.com', 5]]


def test_user_info_query_no_token(main_api, db_conn):
    '''
    Test route to edit pipelines in user dashboard
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, name='Joe Schmoe', email='jschmoe@gmail.com', token='token')
    uid_fake = helper.create_test_user_and_email(db_conn=db_conn, name='Jane Doe', email='fake@gmail.com', token='fake_token')

    data = {
        'query_name': 'user_info',
    }

    response = main_api.post('/api/queries', json=data)
    
    data, status = json.loads(response.data), response.status_code

    assert status == 400
    assert data == 'Invalid query name'


def test_pipeline_uid_query(main_api, db_conn):
    '''
    Test queries route that grabs pipeline info for given token
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, name='Joe Schmoe', email='jschmoe@gmail.com', token='token')
    uid_fake = helper.create_test_user_and_email(db_conn=db_conn, name='Jane Doe', email='fake@gmail.com', token='fake_token')
    cid_google = helper.create_test_company(db_conn=db_conn)
    cid_fb = helper.create_test_company(db_conn=db_conn, name='Facebook')
    pid = helper.create_test_pipeline(db_conn=db_conn, uid=uid, cid=cid_google)
    pid_fake = helper.create_test_pipeline(db_conn=db_conn, uid=uid_fake, cid=cid_fb)

    data = {
        'query_name': 'pipeline_uid',
        'token': 'token'
    }

    response = main_api.post('/api/queries', json=data)

    data, status = json.loads(response.data), response.status_code

    assert status == 200
    result_verify = data[0][1:]
    assert result_verify[0:2] == [pid, cid_google]
    assert "2020-07-17" in result_verify[2]
    assert result_verify[3] == 3
    assert result_verify[4:8] == [None, None, None, None]
    assert "2020-07-21" in result_verify[8]
    assert result_verify[9:] == [1, "Google", "jschmoe@gmail.com", uid]

def test_todos_query_with_pid(main_api, db_conn):
    '''
    Test queries route that grabs pipeline info for given token
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, name='Joe Schmoe', email='jschmoe@gmail.com', token='token')
    cid_google = helper.create_test_company(db_conn=db_conn)
    pid = helper.create_test_pipeline(db_conn=db_conn, uid=uid, cid=cid_google)
    tid = helper.create_test_todo(db_conn=db_conn, uid=uid)
    helper.create_codingchallenge_todo(db_conn=db_conn, pid=pid, tid=tid)

    data = {
        'query_name': 'todo',
        'token': 'token'
    }

    response = main_api.post('/api/queries', json=data)

    data, status = json.loads(response.data), response.status_code

    assert status == 200
    assert data == [[1, None, None, 'Prep for Google interview', 'https://google.com']]

def test_todos_query_without_pid(main_api, db_conn):
    '''
    Test queries route that grabs pipeline info for given token
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, name='Joe Schmoe', email='jschmoe@gmail.com', token='token')
    cid_google = helper.create_test_company(db_conn=db_conn)
    pid = helper.create_test_pipeline(db_conn=db_conn, uid=uid, cid=cid_google)
    tid = helper.create_test_todo(db_conn=db_conn, uid=uid)

    data = {
        'query_name': 'todo',
        'token': 'token'
    }

    response = main_api.post('/api/queries', json=data)

    data, status = json.loads(response.data), response.status_code

    assert status == 200
    assert data == [[2, None, None, 'Prep for Google interview', None]]


def test_bugs_query(main_api, db_conn):
    '''
    Test queries route that grabs all bugs
    '''
    helper.create_test_user_and_email(db_conn=db_conn, name='Joe Schmoe', email='jschmoe@gmail.com', token='token')
    helper.create_bug(db_conn=db_conn, bug="Pursu is down")
    
    data = {
        'query_name': 'bugs',
        'token': 'token'
    }

    response = main_api.post('/api/queries', json=data)

    data, status = json.loads(response.data), response.status_code

    assert status == 200
    assert data == [['Pursu is down']]

def test_redeemed_recruiters_query(main_api, db_conn):
    '''
    Test queries route that grabs all redeemed recruiters
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, name='Joe Schmoe', email='jschmoe@gmail.com', token='token')
    cid_google = helper.create_test_company(db_conn=db_conn)
    rid = helper.create_test_recruiter(db_conn=db_conn, cid=cid_google)
    rid2 = helper.create_test_recruiter(db_conn=db_conn, cid=cid_google, name='Po2', email='jobs2@gmail.com')
    helper.create_test_redeemed_recruiter(db_conn=db_conn, uid=uid, rid=rid)
    
    data = {
        'query_name': 'redeemed_recruiters',
        'token': 'token',
        'cid': cid_google
    }

    response = main_api.post('/api/queries', json=data)

    data, status = json.loads(response.data), response.status_code

    assert status == 200
    assert data == [['Po', 'jobs@gmail.com']]