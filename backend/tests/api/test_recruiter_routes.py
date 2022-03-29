import pytest
import json
import datetime
from email_analysis import LABELS_TO_CATEGORIES, CATEGORIES_TO_LABELS  # pylint: disable=E0401
import api.routes as main_pipeline  # pylint: disable=E0401
import helper  # pylint: disable=E0401


def test_api_add_recruiter(main_api, db_conn):
    '''
    Test route to add a recruiter to a dashboard
    '''
    name = 'Po'
    myEmail = 'jobs@gmail.com'
    company_name = 'Google'
    cid = helper.create_test_company(db_conn=db_conn, name=company_name)

    data = {
        'name': name,
        'email': myEmail,
        'company_name': company_name
    }

    status = main_api.post('/api/recruiter/add', json=data).status_code

    query = "SELECT email, cid FROM recruiters WHERE name='{}';".format(name)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert status == 200
    assert list(db_res) == [myEmail, cid]