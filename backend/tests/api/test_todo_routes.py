import pytest
import json
import datetime
import pytz
from email_analysis import LABELS_TO_CATEGORIES, CATEGORIES_TO_LABELS  # pylint: disable=E0401
import api.routes as main_pipeline  # pylint: disable=E0401
import helper  # pylint: disable=E0401

def test_api_add_todo_dashboard(main_api, db_conn, mocker):
    '''
    Test route to add todo to user dashboard
    '''
    myEmail = 'jschmoe@gmail.com'
    myStage = 'INTERVIEW'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=myEmail)
    cid = helper.create_test_company(db_conn=db_conn)
    company = 'Google'
    coding_challenge_task = 'Complete coding challenge for Google'
    interview_prep_task = "Prep for Google interview"

    data = {
        'token': 'token',
        'task': coding_challenge_task,
        'company': company,
        'deadline': '2020-07-16'
    }

    status = main_api.post('/api/todo/add', json=data).status_code

    query = "SELECT task, company FROM todos WHERE\
         uid={} AND company='{}';".format(uid, company)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert status == 200
    assert list(db_res) == [coding_challenge_task, company]

    # create todo with only required fields
    data['company'] = ""
    data['deadline'] = ""
    data['task'] = interview_prep_task
    status = main_api.post('/api/todo/add', json=data).status_code

    query = "SELECT task, company FROM todos WHERE uid={};".format(uid)
    db_res = helper.execute_test_query(db_conn, query)

    assert status == 200
    assert list(db_res) == [(coding_challenge_task, company), (interview_prep_task, None)]


def test_api_delete_todo_dashboard(main_api, db_conn, mocker):
    '''
    Test route to delete todo from user dashboard
    '''
    myEmail = 'jschmoe@gmail.com'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=myEmail)
    tid = helper.create_test_todo(db_conn=db_conn, uid=uid)

    data = {
        'token': 'token',
        'tid': tid
    }

    status = main_api.post('/api/todo/delete', json=data).status_code

    query = "SELECT task, company FROM todos WHERE tid={};".format(tid)
    db_res = helper.execute_test_query(db_conn, query)

    assert status == 200
    assert db_res == []


def test_api_update_todo_dashboard(main_api, db_conn, mocker):
    '''
    Test route to update todo on user dashboard
    '''
    myEmail = 'jschmoe@gmail.com'
    myStage = CATEGORIES_TO_LABELS['INTERVIEW']
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=myEmail)
    cid = helper.create_test_company(db_conn=db_conn)
    tid = helper.create_test_todo(db_conn=db_conn, uid=uid)
    coding_challenge_task = 'Complete coding challenge for Google'
    company = 'Google'

    data = {
        'token': 'token',
        'tid': tid,
        'company': company,
        'deadline': datetime.datetime(2020, 7, 16, tzinfo=pytz.UTC),
        'task': coding_challenge_task,
    }

    status = main_api.post('/api/todo/update', json=data).status_code

    query = "SELECT company, deadline, task FROM todos WHERE uid={};".format(uid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert status == 200
    assert list(db_res) == [company, datetime.datetime(2020, 7, 16, 0, 0, tzinfo=pytz.UTC), coding_challenge_task]