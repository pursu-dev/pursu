'''Unit tests for trending companies generator'''

import datetime
import helper
from insights import trending_companies

def test_generate_trending_companies_basic(db_conn, appConfig):
    '''
    Tests basic functionality
    One company + trending
    '''
    currentTime = datetime.datetime.now()
    threeDaysAgo = currentTime - datetime.timedelta(days=3)
    fiveDaysAgo = currentTime - datetime.timedelta(days=5)
    tenDaysAgo = currentTime - datetime.timedelta(days=10)

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)

    pid1 = helper.create_test_pipeline(db_conn, uid, cid, stage = 1, timestamp = tenDaysAgo)
    pid2 = helper.create_test_pipeline(db_conn, uid, cid, stage = 1, timestamp = tenDaysAgo)
    pid3 = helper.create_test_pipeline(db_conn, uid, cid, stage = 2, timestamp = fiveDaysAgo)
    pid4 = helper.create_test_pipeline(db_conn, uid, cid, stage = 2, timestamp = fiveDaysAgo)
    pid5 = helper.create_test_pipeline(db_conn, uid, cid, stage = 3, timestamp = threeDaysAgo)
    pid6 = helper.create_test_pipeline(db_conn, uid, cid, stage = 3, timestamp = threeDaysAgo)

    expected_trending = cid

    trending_companies.generate_trends(appConfig)

    query = "SELECT cid FROM trending_companies"
    trending = helper.execute_test_query(db_conn, query)[0][0]

    assert trending == expected_trending

def test_generate_trending_companies_decline(db_conn, appConfig):
    '''
    Tests pipeline changes in a declining activity ratio
    One company with more activity two weeks ago than last week
    '''
    currentTime = datetime.datetime.now()
    threeDaysAgo = currentTime - datetime.timedelta(days=3)
    eightDaysAgo = currentTime - datetime.timedelta(days=8)
    tenDaysAgo = currentTime - datetime.timedelta(days=10)

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)

    pid1 = helper.create_test_pipeline(db_conn, uid, cid, stage = 1, timestamp = tenDaysAgo)
    pid2 = helper.create_test_pipeline(db_conn, uid, cid, stage = 1, timestamp = tenDaysAgo)
    pid3 = helper.create_test_pipeline(db_conn, uid, cid, stage = 2, timestamp = eightDaysAgo)
    pid4 = helper.create_test_pipeline(db_conn, uid, cid, stage = 2, timestamp = eightDaysAgo)
    pid5 = helper.create_test_pipeline(db_conn, uid, cid, stage = 3, timestamp = threeDaysAgo)
    pid6 = helper.create_test_pipeline(db_conn, uid, cid, stage = 3, timestamp = threeDaysAgo)

    expected_trending = []

    trending_companies.generate_trends(appConfig)

    query = "SELECT cid FROM trending_companies"
    trending = helper.execute_test_query(db_conn, query)

    assert trending == expected_trending

def test_generate_trending_companies_consistent(db_conn, appConfig):
    '''
    Tests pipeline changes in a consistent activity ratio
    One company with same activity two weeks ago as last week
    '''
    currentTime = datetime.datetime.now()
    twoDaysAgo = currentTime - datetime.timedelta(days=2)
    threeDaysAgo = currentTime - datetime.timedelta(days=3)
    eightDaysAgo = currentTime - datetime.timedelta(days=8)
    tenDaysAgo = currentTime - datetime.timedelta(days=10)

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)

    pid1 = helper.create_test_pipeline(db_conn, uid, cid, stage = 1, timestamp = tenDaysAgo)
    pid2 = helper.create_test_pipeline(db_conn, uid, cid, stage = 1, timestamp = tenDaysAgo)
    pid3 = helper.create_test_pipeline(db_conn, uid, cid, stage = 2, timestamp = eightDaysAgo)
    pid4 = helper.create_test_pipeline(db_conn, uid, cid, stage = 2, timestamp = eightDaysAgo)
    pid5 = helper.create_test_pipeline(db_conn, uid, cid, stage = 3, timestamp = threeDaysAgo)
    pid6 = helper.create_test_pipeline(db_conn, uid, cid, stage = 3, timestamp = threeDaysAgo)
    pid7 = helper.create_test_pipeline(db_conn, uid, cid, stage = 4, timestamp = twoDaysAgo)
    pid8 = helper.create_test_pipeline(db_conn, uid, cid, stage = 4, timestamp = twoDaysAgo)

    expected_trending = []

    trending_companies.generate_trends(appConfig)

    query = "SELECT cid FROM trending_companies"
    trending = helper.execute_test_query(db_conn, query)

    assert trending == expected_trending

def test_generate_trending_companies_opposites(db_conn, appConfig):
    '''
    Tests companies with opposite trends
    One company trending and one company not trending
    '''
    currentTime = datetime.datetime.now()
    threeDaysAgo = currentTime - datetime.timedelta(days=3)
    fiveDaysAgo = currentTime - datetime.timedelta(days=5)
    eightDaysAgo = currentTime - datetime.timedelta(days=8)
    tenDaysAgo = currentTime - datetime.timedelta(days=10)

    uid = helper.create_test_user_and_email(db_conn)
    cid1 = helper.create_test_company(db_conn, name = "Google")
    cid2 = helper.create_test_company(db_conn, name = "Facebook")

    pid1 = helper.create_test_pipeline(db_conn, uid, cid1, stage = 1, timestamp = tenDaysAgo)
    pid2 = helper.create_test_pipeline(db_conn, uid, cid1, stage = 1, timestamp = tenDaysAgo)
    pid3 = helper.create_test_pipeline(db_conn, uid, cid1, stage = 2, timestamp = fiveDaysAgo)
    pid4 = helper.create_test_pipeline(db_conn, uid, cid1, stage = 2, timestamp = fiveDaysAgo)
    pid5 = helper.create_test_pipeline(db_conn, uid, cid1, stage = 3, timestamp = threeDaysAgo)
    pid6 = helper.create_test_pipeline(db_conn, uid, cid1, stage = 3, timestamp = threeDaysAgo)
    pid7 = helper.create_test_pipeline(db_conn, uid, cid2, stage = 1, timestamp = tenDaysAgo)
    pid8 = helper.create_test_pipeline(db_conn, uid, cid2, stage = 1, timestamp = tenDaysAgo)
    pid9 = helper.create_test_pipeline(db_conn, uid, cid2, stage = 2, timestamp = eightDaysAgo)
    pid10 = helper.create_test_pipeline(db_conn, uid, cid2, stage = 2, timestamp = eightDaysAgo)
    pid11 = helper.create_test_pipeline(db_conn, uid, cid2, stage = 3, timestamp = threeDaysAgo)
    pid12 = helper.create_test_pipeline(db_conn, uid, cid2, stage = 3, timestamp = threeDaysAgo)

    expected_trending = cid1

    trending_companies.generate_trends(appConfig)

    query = "SELECT cid FROM trending_companies"
    trending = helper.execute_test_query(db_conn, query)[0][0]

    assert trending == expected_trending

def test_generate_trending_companies_below_threshold(db_conn, appConfig):
    '''
    Tests case where the number of pipelines is lower than five -- one company + trending with three pipelines (<5 min)
    '''
    currentTime = datetime.datetime.now()
    threeDaysAgo = currentTime - datetime.timedelta(days=3)
    fiveDaysAgo = currentTime - datetime.timedelta(days=5)
    tenDaysAgo = currentTime - datetime.timedelta(days=10)

    uid = helper.create_test_user_and_email(db_conn)
    cid = helper.create_test_company(db_conn)

    pid1 = helper.create_test_pipeline(db_conn, uid, cid, stage = 1, timestamp = tenDaysAgo)
    pid2 = helper.create_test_pipeline(db_conn, uid, cid, stage = 2, timestamp = fiveDaysAgo)
    pid3 = helper.create_test_pipeline(db_conn, uid, cid, stage = 3, timestamp = threeDaysAgo)

    expected_trending = []

    trending_companies.generate_trends(appConfig)

    query = "SELECT cid FROM trending_companies"
    trending = helper.execute_test_query(db_conn, query)

    assert trending == expected_trending
