import pytest
import json
import datetime
from email_analysis import LABELS_TO_CATEGORIES, CATEGORIES_TO_LABELS  # pylint: disable=E0401
import api.utils as utils # pylint: disable=E0401
import helper  # pylint: disable=E0401

def test_user_exists(main_api, db_conn):
    '''
    Unit test for user_exists
    '''
    my_email = 'jschmoe@gmail.com'

    first_resp = utils.user_exists(my_email)
    _uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email)
    second_resp = utils.user_exists(my_email)

    assert first_resp == False
    assert second_resp == True


def test_add_filters(main_api, db_conn, mocker):
    '''
    Unit test to ensure add_filters adds all created filters
    '''
    my_label_id = 'label'
    my_email = 'jschmoe@gmail.com'
    my_queries = ['query1']

    expected_request = {
        'criteria': {
            'query': my_queries[0]
        },
        'action': {
            'addLabelIds': [my_label_id]
        }
    }

    _uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email, label=my_label_id)

    gmail = mocker.MagicMock()
    creds = mocker.MagicMock()
    mocker.patch('apiclient.discovery.build', return_value=gmail)
    filt_request = mocker.patch('shared.filters.get_filters', return_value=my_queries)

    utils.add_filters(creds=creds, email=my_email, label_id=my_label_id)

    filt_request.assert_called_once()
    gmail.users().settings().filters().create.assert_called_once_with(userId=my_email, body=expected_request)


def test_delete_old_user_filters(main_api, db_conn, mocker):
    '''
    Unit test to ensure that deleting old user filters only deletes filters
    associated with adding emails to the pursu-generated gmail label
    '''
    my_label_id = 'label'
    my_email = 'jschmoe@gmail.com'
    _uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email, label=my_label_id)

    filt_list_response = {
        'filter': [
            {   
                'id': 0,
                'action': {'addLabelIds': my_label_id, 'removeLabelIds': 'randomLabel'}
            },
            {
                'id': 1,
                'action': {'addLabelIds': 'randomLabel', 'removeLabelIds': my_label_id}
            }
        ]
    }

    gmail = mocker.MagicMock()
    creds = mocker.MagicMock()
    mocker.patch('apiclient.discovery.build', return_value=gmail)
    gmail.users().settings().filters().list().execute.return_value = filt_list_response
    
    utils.delete_old_user_filters(creds=creds, email=my_email, label_id=my_label_id)

    gmail.users().settings().filters().delete.assert_called_once_with(userId=my_email, id=0)


def test_update_user_filters(main_api, db_conn, mocker):
    '''
    Unit test to ensure updating user filters properly invokes helper functions
    '''
    my_email = 'jschmoe@gmail.com'
    my_label_id = 'label'
    _uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email, label=my_label_id)

    creds = mocker.MagicMock()
    get_creds = mocker.patch('api.utils.get_credentials', return_value=creds)
    delete_filts = mocker.patch('api.utils.delete_old_user_filters', return_value=None)
    add_filts = mocker.patch('api.utils.add_filters', return_value=None)

    utils.update_user_filters(email=my_email, label_id=my_label_id)

    get_creds.assert_called_once_with(my_email, utils.appConfig)
    delete_filts.assert_called_once_with(creds=creds, email=my_email, label_id=my_label_id)
    add_filts.assert_called_once_with(creds=creds, email=my_email, label_id=my_label_id)


def test_transfer_user_account(main_api, db_conn):
    '''
    Unit test for transfer_user_account
    '''
    my_name = 'Joe Schmoe'
    my_email = 'jschmoe@gmail.com'
    my_college = 'University of Michigan'
    my_major = 'Computer Science'
    my_year = 2022
    uid = helper.create_test_user_and_email(db_conn=db_conn, name=my_name, email=my_email, 
          college=my_college, major=my_major, year=my_year)
    
    new_uid = utils.transfer_user_account(uid, my_email)

    # Check that user entry has been transferred
    query1 = "SELECT name, college, major, year FROM users WHERE uid={};".format(new_uid)

    # Check that gmail entry is updated with new uid
    query2 = "SELECT uid FROM gmail WHERE email='{}';".format(my_email)

    # Check that old user entry has been anonymized + deactivated
    query3 = "SELECT name, gender, ethnicity, active FROM users WHERE uid={};".format(uid)
    db_res1 = helper.execute_test_query(db_conn, query1)
    db_res2 = helper.execute_test_query(db_conn, query2)
    db_res3 = helper.execute_test_query(db_conn, query3)
    

    assert list(db_res1[0]) == [my_name, my_college, my_major, my_year]
    assert list(db_res2[0]) == [new_uid]
    assert list(db_res3[0]) == ['ANON', 3, 'ANON', 0]
