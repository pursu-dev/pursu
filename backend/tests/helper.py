''' Helper functions for testing '''
import pytz
import datetime


def execute_test_query(db_conn, query):
    cur = db_conn.cursor()
    cur.execute(query)
    if query.split()[0] == 'SELECT':
        res = cur.fetchall()
        cur.close()
        return res
    else:
        cur.close()


def create_test_user_and_email(db_conn, name='Joe Schmoe', email='jschmoe@gmail.com', token='token', label='label',
                               college='University of Michigan', major='Computer Science', year=2023,
                               gcid=1):
    '''
    Test utility function to create sample user; returns generated UID
    '''
    execute_test_query(db_conn, "INSERT INTO users(name, filt_version, college, major, year) VALUES('{}', 0, '{}', '{}', {});"
                       .format(name, college, major, year))

    uid = execute_test_query(db_conn, "SELECT uid FROM users WHERE name='{}';".format(name))[0][0]
    execute_test_query(db_conn, "INSERT INTO gmail(uid, email, token, label, gcid) \
        VALUES({},'{}','{}','{}',{});".format(uid, email, token, label, gcid))
    return uid


def create_test_company(db_conn, name='Google', filt_version=0, user_created=False, domain=None):
    '''
    Test utility function to create sample company; returns generated CID
    '''
    if domain is None:
        execute_test_query(db_conn, "INSERT INTO companies(name, filt_version, user_created) VALUES('{}', {}, {});".format(
            name, filt_version, int(user_created)))
    else:
        execute_test_query(db_conn, "INSERT INTO companies(name, domain, filt_version, user_created) VALUES('{}', '{}', {}, {});".format(
            name, domain, filt_version, int(user_created)))
    cid = execute_test_query(
        db_conn, "SELECT cid FROM companies WHERE name='{}';".format(name))[0][0]
    return cid


def create_test_pipeline(db_conn, uid, cid, stage=3,
                         timestamp=datetime.datetime(2020, 7, 17, 7, 39, 9, tzinfo=pytz.UTC),
                         deadline=datetime.datetime(2020, 7, 21, 7, 38, 9, tzinfo=pytz.UTC),
                         rid='NULL', years_to_graduate=1):
    '''
    Test utility function to create sample pipeline; returns generated PID
    '''
    execute_test_query(db_conn, "INSERT INTO pipelines(uid, cid, stage, timestamp, deadline, rid) VALUES({}, {}, {}, '{}', '{}', {});".format(
        uid, cid, stage, timestamp, deadline, rid))
    pid = execute_test_query(db_conn, "SELECT pid FROM pipelines WHERE uid={} AND cid={} AND active={};".format(
        uid, cid, 1))[0][0]
    if stage < 5:
        execute_test_query(db_conn, "INSERT INTO stages(uid, cid, stage, timestamp, years_to_graduate) VALUES({}, {}, {}, '{}', {});".format(
            uid, cid, stage, timestamp, years_to_graduate))
    return pid


def create_test_todo(db_conn, uid, task='Prep for Google interview'):
    execute_test_query(db_conn, "INSERT INTO todos(uid, task) VALUES({}, '{}');".format(
        uid, task))
    tid = execute_test_query(db_conn, "SELECT tid FROM todos WHERE uid={} and task='{}';".format(
        uid, task))[0][0]
    return tid


def create_codingchallenge_todo(db_conn, tid, pid, link="https://google.com"):
    execute_test_query(db_conn, "UPDATE pipelines SET link='{}' WHERE pid={};".format(
        link, pid))
    execute_test_query(db_conn, "UPDATE todos SET pid={} WHERE tid={};".format(
        pid, tid))


def create_test_recruiter(db_conn, cid, name='Po', email='jobs@gmail.com'):
    '''
    Test utility function to create sample recruiter; returns generated UID
    '''
    execute_test_query(db_conn, "INSERT INTO recruiters(cid, name, email) VALUES({}, '{}', '{}');".format(
        cid, name, email))
    rid = execute_test_query(
        db_conn, "SELECT rid FROM recruiters WHERE name='{}';".format(name))[0][0]
    return rid

def create_test_redeemed_recruiter(db_conn, uid, rid):
    '''
    Test utility function to create sample recruiter; returns generated UID
    '''
    execute_test_query(db_conn, "INSERT INTO redeemed_recruiters(uid, rid) VALUES({}, '{}');".format(
        uid, rid))


def create_test_college_recruiter_link(db_conn, rid, college='University of Michigan'):
    '''
    Test utility function to create sample college recruiter link
    '''
    execute_test_query(db_conn,
                       "INSERT INTO college_recruiter_link(college, rid) VALUES('{}', {});".format(
                           college, rid))


def create_test_stage_insight(db_conn, num_data_points, uid, cid, duration, stage,
                              timestamp=datetime.date.today() - datetime.timedelta(days=5), years_to_graduate=1):
    '''
    Test utility function to create sample stage insights
    '''
    for _i in range(num_data_points):
        execute_test_query(db_conn, "INSERT INTO stages(uid, cid, stage, duration, timestamp, years_to_graduate) \
        VALUES({}, {}, {}, {}, '{}', {});".format(uid, cid, stage, duration, timestamp, years_to_graduate))

def create_test_google_project(db_conn, appConfig, client_id, client_secret, project_id, topic, has_space=True):
    execute_test_query(db_conn, "INSERT INTO google_projects(project_id, topic, has_space) \
                                 VALUES('{}', '{}', {});".format(
                                     project_id, topic, int(has_space)))
    gcid = execute_test_query(db_conn, "SELECT gcid FROM google_projects\
        WHERE project_id='{}' and topic='{}';".format(project_id, topic))[0][0]
    
    # Add google project to appConfig
    appConfig.GOOGLE_CREDENTIALS.insert(gcid, {
        'CLIENT_ID': client_id,
        'CLIENT_SECRET': client_secret
    })
    return gcid
    
def create_test_stage_insights(db_conn, num_data_points, cid, duration, stage, timestamp):
    '''
    Test utility function to create sample stage insights
    '''
    execute_test_query(db_conn, "INSERT INTO stage_durations (cid, stage, duration, num_stages, min_date, max_date) \
            VALUES ({}, {}, {}, {}, '{}', '{}');".format(cid, stage, duration, num_data_points, timestamp, timestamp))


def create_bug(db_conn, bug='Pursu is down'):
    execute_test_query(db_conn, "INSERT INTO bugs (bug) VALUES('{}');".format(bug))


def create_test_job_listing(db_conn, cid, approved, name, location='Chicago',
                            notes='Notes', link='google.com', internship=True):
    '''
    Test utility function to create test job listing
    '''
    if cid:
        execute_test_query(db_conn, "INSERT INTO jobs(cid, approved, name, location, notes, link, internship) VALUES \
                        ({}, {}, '{}', '{}', '{}', '{}', \
                         {});".format(cid, approved, name, location, notes, link, internship))
    else:
        execute_test_query(db_conn, "INSERT INTO jobs(approved, name, location, notes, link, internship) VALUES \
                        ({}, '{}', '{}', '{}', '{}', {});".format(approved, name, location, notes, link, internship))
    jid = execute_test_query(db_conn, "SELECT jid FROM jobs WHERE name='{}' AND \
                            internship={};".format(name, internship))
    return jid


def award_points_to_new_user(db_conn, uid, num_points):
    execute_test_query(
        db_conn,
        "INSERT INTO referrals(uid, points) VALUES ({}, {});".format(
            uid,
            num_points))


def create_test_referral_entry(db_conn, uid, points=0, redemptions=0):
    '''
    Test utility function to create referral entry
    '''
    execute_test_query(db_conn, "INSERT INTO referrals(uid, points, redemptions) \
        VALUES({}, {}, {})".format(uid, points, redemptions))


def clear_database(db_conn):
    '''
    Pytest utility function to clear database after each test invocation
    '''
    # NOTE: We need to maintain a topological dependency order based on the
    # foreign keys -- use Kahn's algorithm :)
    TABLES = ['jobs', 'data_providers', 'feedback', 'filters', 'stages', 'pipelines',
              'trending_companies', 'redeemed_recruiters', 'referrals',
              'college_recruiter_link', 'recruiters', 'todos', 'companies',
              'gmail', 'users']

    for table in TABLES:
        query = "DELETE FROM {};".format(table)
        execute_test_query(db_conn, query)
