import pytest
import json
import helper  # pylint: disable=E0401
import datetime as datetime
import api.routes as main_pipeline  # pylint: disable=E0401
import insights.update_stage_durations as update_stages
import data_ingestion.routes as main_pipeline  # pylint: disable=E0401


def test_api_edit_dashboard(main_api, mocker, db_conn):
    '''
    Test route to get company recommendations with collaborative filtering
    '''
    query = "ALTER SEQUENCE users_uid_seq RESTART WITH 92"
    _email_res = helper.execute_test_query(db_conn, query)
    uid = helper.create_test_user_and_email(db_conn=db_conn, email='jschmoe@gmail.com')
    cid = helper.create_test_company(db_conn=db_conn)
    _pid = helper.create_test_pipeline(db_conn=db_conn, uid=uid, cid=cid)

    data = {
        'token': 'token'
    }

    aws_client = mocker.MagicMock()
    aws_client.get_recommendations = mocker.MagicMock(return_value={'itemList': [{'itemId': '0'}]})
    mocker.patch('boto3.client', return_value=aws_client)

    status = main_api.post('/api/insights/collaborative_recommendations', json=data).status_code
    assert status == 200

def test_update_insight_data(data_api, mocker, db_conn):
    '''
    Test that update insight data route correctly invokes cron job functions
    '''
    my_call1 = mocker.patch('data_ingestion.routes.pipeline_updates.update_pipelines',
                            return_value=None)
    my_call2 = mocker.patch('data_ingestion.routes.update_stage_durations.update_stage_durations',
                            return_value=None)
    status = data_api.get('/api/data_ingestion/update_stage_insights').status_code
    my_call1.assert_called_once_with(main_pipeline.appConfig)
    my_call2.assert_called_once_with(main_pipeline.appConfig)
    assert status == 200


def test_stage_insights_query(data_api, main_api, mocker, db_conn):
    '''
    Test queries route that grabs stage insights data for given cid and given stage
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, name='Joe Schmoe', email='jschmoe@gmail.com', token='token')
    cid_google = helper.create_test_company(db_conn=db_conn)
    cid_fb = helper.create_test_company(db_conn=db_conn, name='Facebook')

    timestamp = datetime.date.today() - datetime.timedelta(days=5)

    num_data_points = 5
    stage = 1
    for _ in range(0, num_data_points):
        duration = 5
        helper.create_test_stage_insight(db_conn=db_conn, num_data_points=1, uid=uid, cid=cid_google, duration=duration, timestamp=timestamp, stage=stage)
        helper.create_test_stage_insight(db_conn=db_conn, num_data_points=1, uid=uid, cid=cid_fb, duration=7, timestamp=timestamp, stage=3)
    
    
    mocker.patch('data_ingestion.routes.pipeline_updates.update_pipelines',
                            return_value=None)
    response = data_api.get('/api/data_ingestion/update_stage_insights').status_code
    assert response == 200

    data = {
        'cid': cid_google,
        'token': 'token',
    }

    response = main_api.post('/api/insights/get_stage_insights', json=data)

    data, status = json.loads(response.data), response.status_code
    timestamp_str = timestamp.strftime("%m-%d")

    assert status == 200
    assert data[0][0] == stage
    assert data[0][1] == duration
    assert data[0][2] == timestamp_str
    assert data[0][3] == timestamp_str

def test_update_stage_insights(data_api, main_api, mocker, db_conn):
    '''
    Test queries route that grabs stage insights data for given cid and given stage
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, name='Joe Schmoe', email='jschmoe@gmail.com', token='token')
    cid_google = helper.create_test_company(db_conn=db_conn)
    
    num_data_points = 5
    previous_duration = 5
    stage = 1

    prev_timestamp = datetime.date.today() - datetime.timedelta(days=25)

    helper.create_test_stage_insights(db_conn=db_conn, cid=cid_google, num_data_points=num_data_points, stage=stage, timestamp=prev_timestamp.strftime("%m-%d"), duration=previous_duration)
    
    for _ in range(0, num_data_points):
        helper.create_test_stage_insight(db_conn=db_conn, num_data_points=1, uid=uid, cid=cid_google, duration=previous_duration, timestamp=prev_timestamp, stage=stage)

    new_timestamp = datetime.date.today() - datetime.timedelta(days=3)

    for _ in range(0, num_data_points):
        duration = 6
        helper.create_test_stage_insight(db_conn=db_conn, num_data_points=1, uid=uid, cid=cid_google, duration=duration, timestamp=new_timestamp, stage=stage)
    
    
    mocker.patch('data_ingestion.routes.pipeline_updates.update_pipelines',
                            return_value=None)
    response = data_api.get('/api/data_ingestion/update_stage_insights').status_code
    assert response == 200

    data = {
        'cid': cid_google,
        'token': 'test',
    }

    response = main_api.post('/api/insights/get_stage_insights', json=data)
    data, status = json.loads(response.data), response.status_code
    assert status == 400

    data = {
        'cid': cid_google,
        'token': 'token',
    }

    response = main_api.post('/api/insights/get_stage_insights', json=data)

    data, status = json.loads(response.data), response.status_code
    prev_timestamp_str = prev_timestamp.strftime("%m-%d")
    new_timestamp_str = new_timestamp.strftime("%m-%d")
    assert data[0][0] == stage
    assert status == 200
    assert data[0][1] == ((previous_duration * num_data_points) + (duration * num_data_points))/(num_data_points * 2)
    assert data[0][2] == prev_timestamp_str
    assert data[0][3] == new_timestamp_str

def test_find_max_min_dates():
    arg_1 = ["01-01", "02-01", "03-31", "04-02", "05-03", "06-30", "07-02", "08-05", "09-10", "11-12"]
    result_1 = ('06-30', '05-03')
    assert update_stages.find_max_min_dates(arg_1) == result_1
    arg_2 = ["01-01", "02-01", "03-31", "04-02", "05-03", "06-01", "07-02", "08-05", "09-10", "11-12"]
    result_2 = ('07-02', '05-03')
    assert update_stages.find_max_min_dates(arg_2) == result_2
    arg_3 = ["04-02", "01-01", "07-02", "03-31", "11-12", "05-03", "08-05", "06-01", "09-10", "02-01"]
    result_3 = ('07-02', '05-03')
    assert update_stages.find_max_min_dates(sorted(arg_3)) == result_3

def test_redeemed_recruiters(main_api, mocker, db_conn):
    '''
    Test queries route that grabs stage insights data for given cid and given stage
    '''
    uid = helper.create_test_user_and_email(db_conn=db_conn, name='Joe Schmoe', email='jschmoe@gmail.com', token='token')
    cid_google = helper.create_test_company(db_conn=db_conn)
    rid = helper.create_test_recruiter(db_conn=db_conn, cid=cid_google)

    data = {
        'cid': cid_google,
        'token': 'token',
    }
    
    response = main_api.post('/api/insights/get_redeemed_recruiter_data', json=data)
    response_data, status = response.data, response.status_code
    assert status == 200
    assert response_data == b'true'

    helper.create_test_redeemed_recruiter(db_conn=db_conn, uid=uid, rid=rid)

    response = main_api.post('/api/insights/get_redeemed_recruiter_data', json=data)
    response_data, status = response.data, response.status_code
    assert status == 200
    assert response_data == b'false'
