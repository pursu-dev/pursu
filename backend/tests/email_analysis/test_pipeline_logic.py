'''Unit tests for pipeline_logic module in email_analysis'''
import email_analysis.pipeline_logic as pipeline_logic  # pylint: disable=E0401
from email_analysis import LABELS_TO_CATEGORIES, CATEGORIES_TO_LABELS  # pylint: disable=E0401
import helper  # pylint: disable=E0401
import json
import datetime
import pytz


def test_inserting_new_pipeline(email_api, db_conn, mocker):
    '''
    Test for inserting an application confirmation into pipelines table as an
    entry point to previously non-existent pipeline
    '''
    email_response = {
        'company': 'Google',
        'timestamp': datetime.datetime(2020, 7, 16, 7, 41, 10, tzinfo=pytz.UTC),
        'deadline': datetime.datetime(2020, 7, 16, tzinfo=pytz.UTC)
    }
    category = 0
    user_email = 'jschmoe@gmail.com'

    link_update = mocker.patch(
        'email_analysis.pipeline_logic.update_link', return_value=None)

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)
    rid = helper.create_test_recruiter(db_conn, cid)

    email_response['rid'] = rid
    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT uid, cid, stage, active, timestamp, deadline, rid FROM pipelines \
        WHERE uid={};".format(uid)
    pipeline_db_res = helper.execute_test_query(db_conn, query)[0]

    query = "SELECT uid,cid,stage,years_to_graduate,timestamp FROM stages WHERE uid={};".format(
        uid)
    stage_db_res = helper.execute_test_query(db_conn, query)[0]

    link_update.assert_called_once()
    assert list(pipeline_db_res) == [uid, cid, category, 1,
                                     email_response['timestamp'], email_response['deadline'], rid]
    assert list(stage_db_res) == [uid, cid, category,
                                  1, email_response['timestamp']]


def test_inserting_new_pipeline_pre_app(email_api, db_conn):
    '''
    Fix: 8/26/20
    Bug: pid is undefined if we insert a new pipeline in a PRE_APP, or OFFER stage
    '''
    email_response = {
        'company': 'Google',
        'deadline': '2020-07-16',
        'timestamp': '2020-07-16 07:41:10',
        'rid': None
    }
    category = CATEGORIES_TO_LABELS['PRE_APP']
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)
    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT uid, cid, stage FROM pipelines WHERE uid={};".format(uid)
    pipeline_db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(pipeline_db_res) == [uid, cid, category]


def test_stage_advancement_with_multiple_companies_in_pipeline(email_api, db_conn):
    '''
    Baseline test for advancing a user's pipeline while other pipelines are active
    '''
    email_response = {
        'company': 'Google',
        'timestamp': datetime.datetime(2020, 7, 21, 7, 38, 9, tzinfo=pytz.UTC),
        'deadline': None,
        'rid': None
    }
    category = 3
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    cid_fb = helper.create_test_company(db_conn, name='Facebook')
    cid_google = helper.create_test_company(db_conn)
    timestamp = datetime.datetime(2020, 7, 19, 7, 39, 9, tzinfo=pytz.UTC)
    pid_fb = helper.create_test_pipeline(
        db_conn, uid, cid_fb, CATEGORIES_TO_LABELS['APPLICATION_CONF'])
    pid_google = helper.create_test_pipeline(db_conn, uid, cid_google, CATEGORIES_TO_LABELS['APPLICATION_CONF'],
                                             timestamp=timestamp)

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT uid, cid, stage, active FROM pipelines \
        WHERE pid={};".format(pid_google)
    db_res = helper.execute_test_query(db_conn, query)[0]

    query = "SELECT uid, cid, stage, active FROM pipelines \
        WHERE pid={};".format(pid_fb)
    db_res_2 = helper.execute_test_query(db_conn, query)[0]

    query = "SELECT uid, cid, stage, years_to_graduate, timestamp FROM stages \
        WHERE uid={} AND cid={} AND stage={};".format(uid, cid_google, category)
    db_res_3 = helper.execute_test_query(db_conn, query)[0]

    query = "SELECT uid, cid, stage, years_to_graduate, timestamp, duration FROM stages \
        WHERE uid={} AND cid={} AND stage={};".format(uid, cid_google, CATEGORIES_TO_LABELS['APPLICATION_CONF'])
    db_res_4 = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [uid, cid_google, category, 1]

    assert list(db_res_2) == [uid, cid_fb,
                              CATEGORIES_TO_LABELS['APPLICATION_CONF'], 1]

    assert list(db_res_3) == [uid, cid_google, category,
                              1, email_response['timestamp']]

    assert list(db_res_4) == [uid, cid_google, CATEGORIES_TO_LABELS['APPLICATION_CONF'], 1,
                              timestamp, 1]


def test_pipeline_advancement_when_inactive_duplicate_company_exists(email_api, db_conn):
    '''
    Test for when there are two pipelines for the same uid, cid pair but one pipeline
    is inactive. Active pipeline should be the one that's updated
    '''
    email_response = {
        'company': 'Google',
        'timestamp': datetime.datetime(2020, 7, 27, 7, 39, 9, tzinfo=pytz.UTC),
        'deadline': None,
        'rid': None
    }
    category = 6
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)

    helper.create_test_pipeline(db_conn, uid, cid)

    query = 'UPDATE pipelines SET active={} WHERE uid={};'.format(0, uid)
    helper.execute_test_query(db_conn, query)

    pid = helper.create_test_pipeline(
        db_conn, uid, cid, CATEGORIES_TO_LABELS['APPLICATION_CONF'])

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT uid, cid, stage, active FROM pipelines \
        WHERE pid={};".format(pid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [uid, cid, category, 1]


def test_pipeline_not_advancing_after_offer_or_rejection(email_api, db_conn):
    '''
    Test that pipeline doesn't update after an offer or rejection exists
    '''
    email_response = {
        'company': 'Google',
        'timestamp': '2020-07-17 07:39:09',
        'deadline': None,
        'rid': None
    }
    category = 6
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)
    pid = helper.create_test_pipeline(db_conn, uid, cid, CATEGORIES_TO_LABELS['OFFER'],
                                      timestamp='2020-07-15 06:36:15')

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT uid, cid, stage, active FROM pipelines \
        WHERE pid={};".format(pid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    query = "SELECT uid,cid,stage,years_to_graduate,timestamp,duration \
        FROM stages WHERE uid={};".format(uid)
    db_res_2 = helper.execute_test_query(db_conn, query)

    assert list(db_res) == [uid, cid, CATEGORIES_TO_LABELS['OFFER'], 1]

    assert db_res_2 == []


def test_pipeline_no_update_irrelevant_postoffer(email_api, db_conn):
    '''
    Test to confirm that irrelevant and post-offer emails don't affect pipeline
    '''
    email_response = {
        'company': 'Google',
        'timestamp': '2020-07-17 07:39:09',
        'rid': None
    }
    category = -1
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)

    pid = pipeline_logic.update_pipeline(email_response, category, user_email)
    query = "SELECT uid, cid, stage, active FROM pipelines \
        WHERE pid={};".format(pid)
    db_res = helper.execute_test_query(db_conn, query)

    assert db_res == []

    query = "SELECT uid,cid,stage,years_to_graduate,timestamp \
        FROM stages WHERE uid={};".format(uid)
    helper.execute_test_query(db_conn, query)

    assert db_res == []


def test_pipeline_updates_after_preapplication(email_api, db_conn):
    '''
    Test to confirm that future updates to pipeline occur if current stage is pre-application
    '''
    email_response = {
        'company': 'Google',
        'timestamp': datetime.datetime(2020, 7, 17, 7, 39, 9, tzinfo=pytz.UTC),
        'deadline': None,
        'rid': None
    }
    category = 0
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)
    timestamp = datetime.datetime(2020, 7, 11, 7, 39, 9, tzinfo=pytz.UTC)
    pid = helper.create_test_pipeline(db_conn, uid, cid, CATEGORIES_TO_LABELS['PRE_APP'],
                                      timestamp=timestamp)

    pipeline_logic.update_pipeline(email_response, category, user_email)
    query = "SELECT uid, cid, stage, active, timestamp FROM pipelines \
        WHERE pid={};".format(pid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [uid, cid, category, 1,
                            email_response['timestamp']]

    query = "SELECT uid,cid,stage,years_to_graduate,timestamp,duration FROM stages \
        WHERE uid={} AND cid={} AND stage={};".format(uid, cid, category)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [uid, cid, category, 1,
                            email_response['timestamp'], None]


def test_pipeline_updates_after_todo(email_api, db_conn):
    '''
    Test to confirm that future updates to pipeline occur if current stage is todo
    '''
    email_response = {
        'company': 'Google',
        'timestamp': datetime.datetime(2020, 7, 17, 7, 39, 9, tzinfo=pytz.UTC),
        'deadline': None,
        'rid': None
    }
    category = 0
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)
    timestamp = datetime.datetime(2020, 7, 11, 7, 39, 9, tzinfo=pytz.UTC)
    pid = helper.create_test_pipeline(db_conn, uid, cid, CATEGORIES_TO_LABELS['TODO'],
                                      timestamp=timestamp)

    pipeline_logic.update_pipeline(email_response, category, user_email)
    query = "SELECT uid, cid, stage, active, timestamp FROM pipelines \
        WHERE pid={};".format(pid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [uid, cid, category, 1,
                            email_response['timestamp']]

    query = "SELECT uid,cid,stage,years_to_graduate,timestamp,duration FROM stages \
        WHERE uid={} AND cid={} AND stage={};".format(uid, cid, category)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [uid, cid, category, 1,
                            email_response['timestamp'], None]


def test_insights_update_after_rejection(email_api, db_conn):
    '''
    Test to confirm that after a rejection email, insights table adds duration for previous stage and new entry for rejection
    '''

    email_response = {
        'company': 'Google',
        'timestamp': datetime.datetime(2020, 7, 17, 7, 39, 9, tzinfo=pytz.UTC),
        'deadline': None,
        'rid': None
    }
    category = 6
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)
    timestamp = datetime.datetime(2020, 7, 11, 7, 39, 9, tzinfo=pytz.UTC)
    pid = helper.create_test_pipeline(db_conn, uid, cid, CATEGORIES_TO_LABELS['INTERVIEW'],
                                      timestamp=timestamp)

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT uid,cid,stage,years_to_graduate,timestamp,duration FROM stages \
        WHERE uid={} AND cid={} AND stage={};".format(uid, cid, CATEGORIES_TO_LABELS['INTERVIEW'])
    db_res = helper.execute_test_query(db_conn, query)[0]

    query = "SELECT uid,cid,stage,years_to_graduate,timestamp,duration FROM stages \
        WHERE uid={} AND cid={} AND stage={};".format(uid, cid, category)
    stage_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [
        uid,
        cid,
        CATEGORIES_TO_LABELS['INTERVIEW'],
        1,
        timestamp,
        6]

    assert list(stage_res) == [
        uid,
        cid,
        category,
        1,
        email_response['timestamp'],
        None
    ]


def test_insights_not_update_after_same_stage(email_api, db_conn):
    '''
    Test to confirm that after an email is received that indicates the user is in the same stage, insights table is not updated
    '''

    email_response = {
        'company': 'Google',
        'timestamp': datetime.datetime(2020, 7, 17, 7, 39, 9, tzinfo=pytz.UTC),
        'deadline': None,
        'rid': None
    }
    category = CATEGORIES_TO_LABELS['INTERVIEW']
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)
    timestamp = datetime.datetime(2020, 7, 11, 7, 39, 9, tzinfo=pytz.UTC)
    helper.create_test_pipeline(db_conn, uid, cid, CATEGORIES_TO_LABELS['INTERVIEW'],
                                timestamp=timestamp)

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT years_to_graduate, timestamp FROM stages \
        WHERE uid={} AND cid={} AND stage={};".format(uid, cid, CATEGORIES_TO_LABELS['INTERVIEW'])
    db_res = helper.execute_test_query(db_conn, query)

    assert len(db_res) == 1
    assert list(db_res[0]) == [1, timestamp]


def test_insights_updates_duration(email_api, db_conn):
    '''
    Test to confirm that when a pipeline is advanced, insights is updated with the correct duration of old stage and new stage is inserted
    '''
    email_response = {
        'company': 'Google',
        'timestamp': datetime.datetime(2020, 7, 17, 7, 39, 9, tzinfo=pytz.UTC),
        'deadline': None,
        'rid': None
    }
    category = CATEGORIES_TO_LABELS['CODING_CHALLENGE']
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)
    timestamp = datetime.datetime(2020, 7, 11, 7, 39, 9, tzinfo=pytz.UTC)
    helper.create_test_pipeline(db_conn, uid, cid, CATEGORIES_TO_LABELS['APPLICATION_CONF'],
                                timestamp=timestamp)

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT years_to_graduate, timestamp, duration FROM stages WHERE \
        uid={} AND cid={} AND stage={};".format(uid, cid, CATEGORIES_TO_LABELS['APPLICATION_CONF'])
    db_res = helper.execute_test_query(db_conn, query)[0]

    query = "SELECT years_to_graduate, timestamp, duration FROM stages WHERE \
        uid={} AND cid={} AND stage={};".format(uid, cid, category)
    db_res_2 = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [1, timestamp, 6]
    assert list(db_res_2) == [1, email_response['timestamp'], None]


def test_pipeline_handles_empty_company_field(email_api, db_conn):
    '''
    Test to ensure that update pipeline does not break if email is incorrectly parsed/company is not parseable
    '''
    email_response = {
        'company': None,
        'timestamp': '2020-07-17',
        'rid': None
    }

    category = 0
    user_email = 'jschmoe@gmail.com'

    _uid = helper.create_test_user_and_email(db_conn)
    _cid = helper.create_test_company(db_conn)
    _pid = helper.create_test_pipeline(
        db_conn, _uid, _cid, CATEGORIES_TO_LABELS['TODO'])

    pid = pipeline_logic.update_pipeline(email_response, category, user_email)

    assert pid == -1


def test_insert_todo_after_coding_challenge(email_api, db_conn):
    '''
    Test to ensure that when a coding challenge is received, user's todo table is updated
    '''
    email_response = {
        'company': 'Google',
        'deadline': datetime.datetime(2020, 7, 16, tzinfo=pytz.UTC),
        'timestamp': datetime.datetime(2020, 7, 16, 7, 41, 10, tzinfo=pytz.UTC),
        'rid': None
    }
    category = 2
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    helper.create_test_company(db_conn)

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT company, deadline, task FROM todos \
        WHERE uid={};".format(uid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [email_response['company'], email_response['deadline'], 'Complete coding challenge']

def test_pid_in_todos(email_api, db_conn):
    '''
    Test to ensure that when a coding challenge is received, user's todo table is updated
    '''
    email_response = {
        'company': 'Google',
        'deadline': datetime.datetime(2020, 7, 16, tzinfo=pytz.UTC),
        'timestamp': datetime.datetime(2020, 7, 16, 7, 41, 10, tzinfo=pytz.UTC),
        'rid': None
    }
    category = 2
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    helper.create_test_company(db_conn)

    pid = pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT pid FROM todos \
        WHERE uid={};".format(uid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [pid]


def test_insert_todo_after_offer(email_api, db_conn):
    '''
    Test to ensure that when an offer is received, user's todo table is updated
    '''
    email_response = {
        'company': 'Google',
        'deadline': datetime.datetime(2020, 7, 16, tzinfo=pytz.UTC),
        'timestamp': datetime.datetime(2020, 7, 16, 7, 41, 10, tzinfo=pytz.UTC),
        'rid': None
    }
    category = 5
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    helper.create_test_company(db_conn)

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT company, deadline, task FROM todos \
        WHERE uid={};".format(uid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [email_response['company'], email_response['deadline'], 'Review offer']


def test_insert_todo_after_interview(email_api, db_conn):
    '''
    Test to ensure that when an interview is received, user's todo table is updated
    '''
    email_response = {
        'company': 'Google',
        'deadline': datetime.datetime(2020, 7, 16, tzinfo=pytz.UTC),
        'timestamp': datetime.datetime(2020, 7, 16, 7, 41, 10, tzinfo=pytz.UTC),
        'rid': None
    }
    category = 3
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    helper.create_test_company(db_conn)

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT company, deadline, task FROM todos \
        WHERE uid={};".format(uid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [email_response['company'], email_response['deadline'], 'Prepare for interview']


def test_insert_todo_after_rejection(email_api, db_conn):
    '''
    Test to ensure that when a rejection is received, user's todo table is not updated
    '''
    email_response = {
        'company': 'Google',
        'deadline': '2020-07-16',
        'timestamp': '2020-07-16 07:41:10',
        'rid': None
    }
    category = 6
    user_email = 'jschmoe@gmail.com'

    helper.create_test_user_and_email(db_conn)
    helper.create_test_company(db_conn)

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT * FROM todos;"
    db_res = helper.execute_test_query(db_conn, query)

    assert db_res == []


def test_update_link_for_coding_challenge_email(email_api, db_conn):
    '''
    Unit test to ensure that pipelines are updated with coding challenge links
    '''
    my_link = 'https://test_link'
    my_email = 'jschmoe@gmail.com'
    my_company = 'Google'
    my_stage = CATEGORIES_TO_LABELS['CODING_CHALLENGE']
    email_response = {
        'company': my_company,
        'deadline': '2020-07-16',
        'timestamp': '2020-07-16 07:41:10',
        'challenge_link': my_link,
        'rid': None
    }

    uid = helper.create_test_user_and_email(db_conn=db_conn, email=my_email)
    cid = helper.create_test_company(db_conn=db_conn, name=my_company)
    pid = helper.create_test_pipeline(
        db_conn=db_conn, uid=uid, cid=cid, stage=my_stage)

    pipeline_logic.update_link(email_response, pid, my_stage)

    query = "SELECT link FROM pipelines WHERE pid={}".format(pid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [my_link]


def test_update_link_for_stage_not_coding_challenge(email_api, db_conn):
    '''
    Ensure that update_link sets the link field to null if the stage is not
    coding challenge, or no link was parseable
    '''
    my_link = 'https://test_link'
    my_email = 'jschmoe@gmail.com'
    first_company = 'Google'
    second_company = 'Facebook'
    my_first_stage = CATEGORIES_TO_LABELS['CODING_CHALLENGE']
    my_second_stage = CATEGORIES_TO_LABELS['INTERVIEW']

    first_email_response = {}
    second_email_response = {'challenge_link': my_link}

    uid = helper.create_test_user_and_email(
        db_conn=db_conn, email=my_email, name='Joe')
    cid1 = helper.create_test_company(db_conn=db_conn, name=first_company)
    cid2 = helper.create_test_company(db_conn=db_conn, name=second_company)
    pid1 = helper.create_test_pipeline(
        db_conn=db_conn, uid=uid, cid=cid1, stage=my_first_stage)
    pid2 = helper.create_test_pipeline(
        db_conn=db_conn, uid=uid, cid=cid2, stage=my_second_stage)

    pipeline_logic.update_link(
        first_email_response, pid2, my_first_stage)
    query = "SELECT link FROM pipelines WHERE pid={}".format(pid1)
    first_db_res = helper.execute_test_query(db_conn, query)[0]

    pipeline_logic.update_link(
        second_email_response, pid2, my_second_stage)
    query = "SELECT link FROM pipelines WHERE pid={}".format(pid2)
    second_db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(first_db_res) == [None]
    assert list(second_db_res) == [None]


def test_stages_update_with_no_year(email_api, db_conn):
    email_response = {
        'company': 'Google',
        'timestamp': datetime.datetime(2020, 7, 16, 7, 41, 10, tzinfo=pytz.UTC),
        'deadline': datetime.datetime(2020, 7, 16, tzinfo=pytz.UTC)
    }
    category = 0
    user_name = 'Joe Schmoe'
    user_email = 'jschmoe@gmail.com'

    cid = helper.create_test_company(db_conn)
    rid = helper.create_test_recruiter(db_conn, cid)
    email_response['rid'] = rid

    helper.execute_test_query(db_conn, "INSERT INTO users(name, filt_version, college, major) VALUES('{}', 0, '{}', '{}');"
                       .format(user_name, 'University', 'CS'))

    uid = helper.execute_test_query(db_conn, "SELECT uid FROM users WHERE name='{}';".format(user_name))[0][0]
    helper.execute_test_query(db_conn, "INSERT INTO gmail(uid, email, token, label) \
        VALUES({},'{}','{}','{}');".format(uid, user_email, 'token', 'label'))

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT uid,cid,stage,years_to_graduate,timestamp FROM stages WHERE uid={};".format(
        uid)
    stage_db_res = helper.execute_test_query(db_conn, query)

    assert list(stage_db_res) == []


def test_todo_insertion_with_no_deadline(email_api, db_conn):
    '''
    Test to ensure that when an interview is received, user's todo table is updated
    '''
    email_response = {
        'company': 'Google',
        'deadline': None,
        'timestamp': datetime.datetime(2020, 7, 16, 7, 41, 10, tzinfo=pytz.UTC),
        'rid': None
    }
    category = 3
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    helper.create_test_company(db_conn)

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT company, deadline, task FROM todos \
        WHERE uid={};".format(uid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [email_response['company'], datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC), 'Prepare for interview']


def test_todo_insertion_with_deadline_four_months_away(email_api, db_conn):
    '''
    Test to ensure that when an interview is received, user's todo table is updated
    '''
    email_response = {
        'company': 'Google',
        'deadline': datetime.datetime(2025, 2, 16, 7, 41, 10, tzinfo=pytz.UTC),
        'timestamp': datetime.datetime(2020, 7, 16, 7, 41, 10, tzinfo=pytz.UTC),
        'rid': None
    }
    category = 3
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    helper.create_test_company(db_conn)

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT company, deadline, task FROM todos \
        WHERE uid={};".format(uid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [email_response['company'], datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC), 'Prepare for interview']


def test_pipeline_updates_after_duplicate_interview(email_api, db_conn):
    '''
    Test to ensure that if a duplicate interview email is received, contextual information will be updated
    '''
    email_response = {
        'company': 'Google',
        'timestamp': datetime.datetime(2020, 7, 21, 7, 38, 9, tzinfo=pytz.UTC),
        'deadline': datetime.datetime(2020, 7, 31, 7, 38, 9, tzinfo=pytz.UTC),
    }
    category = 3
    user_email = 'jschmoe@gmail.com'

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)
    rid = helper.create_test_recruiter(db_conn, cid)
    email_response['rid'] = helper.create_test_recruiter(db_conn, cid, name='Shifu', email='email@gmail.com')
    timestamp = datetime.datetime(2020, 7, 19, 7, 39, 9, tzinfo=pytz.UTC)
    deadline = datetime.datetime(2020, 7, 30, 7, 38, 9, tzinfo=pytz.UTC)
    pid = helper.create_test_pipeline(db_conn, uid, cid, CATEGORIES_TO_LABELS['INTERVIEW'],
                                             timestamp=timestamp, deadline=deadline, rid=rid)

    pipeline_logic.update_pipeline(email_response, category, user_email)

    query = "SELECT uid, cid, stage, timestamp, deadline, rid FROM pipelines \
        WHERE pid={};".format(pid)
    db_res = helper.execute_test_query(db_conn, query)[0]

    assert list(db_res) == [uid, cid, category, email_response['timestamp'], email_response['deadline'], email_response['rid']]
