import pytest
import json
import datetime
from email_analysis import LABELS_TO_CATEGORIES, CATEGORIES_TO_LABELS  # pylint: disable=E0401
import api.routes as main_pipeline  # pylint: disable=E0401
import helper  # pylint: disable=E0401


def test_beta_feedback(main_api, db_conn):
    '''
    Test route to add beta feedback
    '''
    myEmail = 'jschmoe@gmail.com'
    uid = helper.create_test_user_and_email(db_conn=db_conn, email=myEmail)
    feedback = "Pursu sucks!"

    data = {
        'email': myEmail,
        'comment': feedback
    }

    status = main_api.post('/api/beta/feedback', json=data).status_code

    query = "SELECT comment FROM feedback WHERE email='{}';".format(myEmail)
    db_res = helper.execute_test_query(db_conn, query)[0][0]

    assert status == 200
    assert db_res == feedback