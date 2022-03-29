'''Unit tests for stage durations table'''

import datetime
import pytz
import helper # pylint: disable=E0401
from insights.update_stage_durations import update_stage_durations # pylint: disable=E0401


def test_update_stage_durations_basic(db_conn, appConfig):
    '''
    Sanity test for updating stage_durations table
    '''

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)

    num_data_points = 5
    app_conf_duration = 10
    helper.create_test_stage_insight(db_conn, num_data_points, uid, cid, app_conf_duration, stage=0)

    coding_challenge_duration = 7
    helper.create_test_stage_insight(db_conn, num_data_points, uid, cid, coding_challenge_duration, stage=2)

    interview_duration = 3
    helper.create_test_stage_insight(db_conn, num_data_points, uid, cid, interview_duration, stage=3)
    
    update_stage_durations(appConfig)

    query = "SELECT duration FROM stage_durations WHERE cid={} AND stage={}".format(cid, 0)
    avg_app_conf_duration = helper.execute_test_query(db_conn, query)[0][0]

    query = "SELECT duration FROM stage_durations WHERE cid={} AND stage={}".format(cid, 2)
    avg_coding_challenge_duration = helper.execute_test_query(db_conn, query)[0][0]

    query = "SELECT duration FROM stage_durations WHERE cid={} AND stage={}".format(cid, 3)
    avg_interview_duration = helper.execute_test_query(db_conn, query)[0][0]

    full_pipeline_duration = app_conf_duration + coding_challenge_duration + interview_duration
    query = "SELECT duration FROM stage_durations WHERE cid={} AND stage={}".format(cid, -1)
    avg_full_pipeline_duration = helper.execute_test_query(db_conn, query)[0][0]

    assert avg_app_conf_duration == app_conf_duration
    assert avg_coding_challenge_duration == coding_challenge_duration
    assert avg_interview_duration == interview_duration
    assert avg_full_pipeline_duration == full_pipeline_duration


def test_update_stage_durations_app_conf_and_referral(db_conn, appConfig):
    '''
    Test to ensure that duration between app_conf and referral is calculated
    '''

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)

    num_data_points = 5
    app_conf_duration = 10
    helper.create_test_stage_insight(db_conn, num_data_points, uid, cid, app_conf_duration, stage=0)

    referral_duration = 8
    helper.create_test_stage_insight(db_conn, num_data_points, uid, cid, referral_duration, stage=1)

    coding_challenge_duration = 7
    helper.create_test_stage_insight(db_conn, num_data_points, uid, cid, coding_challenge_duration, stage=2)

    interview_duration = 3
    helper.create_test_stage_insight(db_conn, num_data_points, uid, cid, interview_duration, stage=3)
    
    update_stage_durations(appConfig)

    query = "SELECT duration FROM stage_durations WHERE cid={} AND stage={}".format(cid, 0)
    avg_app_conf_duration = helper.execute_test_query(db_conn, query)[0][0]

    query = "SELECT duration FROM stage_durations WHERE cid={} AND stage={}".format(cid, 1)
    avg_referral_duration = helper.execute_test_query(db_conn, query)[0][0]

    full_pipeline_duration = ((app_conf_duration + referral_duration) / 2) + coding_challenge_duration + interview_duration
    query = "SELECT duration FROM stage_durations WHERE cid={} AND stage={}".format(cid, -1)
    avg_full_pipeline_duration = helper.execute_test_query(db_conn, query)[0][0]

    assert avg_app_conf_duration == app_conf_duration
    assert avg_referral_duration == referral_duration
    assert avg_full_pipeline_duration == full_pipeline_duration

def test_update_stage_durations_basic_multiple_users(db_conn, appConfig):
    '''
    Sanity test for updating stage_durations table
    '''

    uid = helper.create_test_user_and_email(db_conn)
    uid2 = helper.create_test_user_and_email(db_conn, name='Jane Doe', email='jdoe@umich.edu', token='token2')
    cid = helper.create_test_company(db_conn)

    num_data_points = 5
    app_conf_duration, app_conf_duration2 = 10, 12
    helper.create_test_stage_insight(db_conn, num_data_points, uid, cid, app_conf_duration, stage=0)
    helper.create_test_stage_insight(db_conn, num_data_points, uid2, cid, app_conf_duration2, stage=0)

    coding_challenge_duration, coding_challenge_duration2 = 7, 9
    helper.create_test_stage_insight(db_conn, num_data_points, uid, cid, coding_challenge_duration, stage=2)
    helper.create_test_stage_insight(db_conn, num_data_points, uid2, cid, coding_challenge_duration2, stage=2)

    interview_duration = 3
    helper.create_test_stage_insight(db_conn, num_data_points, uid, cid, interview_duration, stage=3)
    
    update_stage_durations(appConfig)

    query = "SELECT duration FROM stage_durations WHERE cid={} AND stage={}".format(cid, 0)
    avg_app_conf_duration = helper.execute_test_query(db_conn, query)[0][0]

    query = "SELECT duration FROM stage_durations WHERE cid={} AND stage={}".format(cid, 2)
    avg_coding_challenge_duration = helper.execute_test_query(db_conn, query)[0][0]

    query = "SELECT duration FROM stage_durations WHERE cid={} AND stage={}".format(cid, 3)
    avg_interview_duration = helper.execute_test_query(db_conn, query)[0][0]

    full_pipeline_duration = (app_conf_duration + app_conf_duration2) / 2 + \
        (coding_challenge_duration + coding_challenge_duration2) / 2 + interview_duration
    query = "SELECT duration FROM stage_durations WHERE cid={} AND stage={}".format(cid, -1)
    avg_full_pipeline_duration = helper.execute_test_query(db_conn, query)[0][0]

    assert avg_app_conf_duration == (app_conf_duration + app_conf_duration2) / 2
    assert avg_coding_challenge_duration == (coding_challenge_duration + coding_challenge_duration2) / 2
    assert avg_interview_duration == interview_duration
    assert avg_full_pipeline_duration == full_pipeline_duration
