"""Houses logic for updating pipelines and stages from new email entry"""
from datetime import datetime
import pytz
from psycopg2 import sql
from email_analysis import appConfig
from email_analysis import LABELS_TO_CATEGORIES, CATEGORIES_TO_LABELS
#pylint: disable=too-many-arguments


def update_pipeline(email_resp, category, user_email):
    """
    Updates user pipeline based on given email categorization.
    PRECONDITION: there is only one unique active pipeline for every uid,cid pair
    """
    labels_to_ignore = ['IRRELEVANT', 'POST_OFFER']
    if LABELS_TO_CATEGORIES[category] in labels_to_ignore:
        return -1

    query = sql.SQL("SELECT uid FROM gmail WHERE email={}").format(sql.Literal(user_email))
    db_res = appConfig.DB_CONN.execute_select_query(query)
    if db_res == []:
        print("ERROR: Cannot update pipeline -- uid for {} does not exist".format(user_email))
        return -1
    uid = db_res[0][0]

    company = email_resp['company']
    if company is None:
        return -1

    query = sql.SQL("SELECT cid FROM companies WHERE UPPER(name)=UPPER({})").format(
        sql.Literal(company))
    db_res = appConfig.DB_CONN.execute_select_query(query)
    if db_res == []:
        print("ERROR: Cannot update pipeline -- cid for {} does not exist".format(company))
        return -1
    cid = db_res[0][0]

    # TODO: error checking for more than one active pipeline
    query = sql.SQL("SELECT stage, pid FROM pipelines WHERE uid={} AND cid={} AND active=1").format(
        sql.Literal(uid), sql.Literal(cid))
    response = appConfig.DB_CONN.execute_select_query(query)

    timestamp = email_resp['timestamp']
    deadline = email_resp['deadline'] if email_resp['deadline'] is not None else 'epoch'
    rid = email_resp['rid']

    if response != []:
        current_stage, pid = response[0][0], response[0][1]
    else:
        pid = insert_new_pipeline(uid, cid, category, timestamp, deadline, rid)
        insert_todo(uid, pid, company, deadline, category)
        update_link(email_resp, pid, category)
        insert_into_insights(uid, cid, category, timestamp)
        current_stage = CATEGORIES_TO_LABELS['OFFER']

    if not compare_stages(current_stage, CATEGORIES_TO_LABELS['OFFER']):
        return pid

    update_link(email_resp, pid, category)

    if compare_stages(current_stage, category):
        # TODO: let front-end prompt user to confirm deactivation of pipeline after stage 5 or 6
        update_pipeline_info(timestamp, category, deadline, pid, rid)
        insert_todo(uid, pid, company, deadline, category)
        update_insights(uid, cid, timestamp, category, current_stage)
    elif category == current_stage:
        update_pipeline_info(timestamp, category, deadline, pid, rid)

    return pid


def update_pipeline_info(timestamp, category, deadline, pid, rid):
    '''
    Updates pipeline with parsed contextual information
    '''
    query = sql.SQL("UPDATE pipelines SET timestamp={}, stage={}, deadline={} \
            WHERE pid={};").format(sql.Literal(timestamp), sql.Literal(category),
                                   sql.Literal(deadline), sql.Literal(pid))
    appConfig.DB_CONN.execute_update_query(query)

    if rid is not None:
        query = sql.SQL("UPDATE pipelines SET rid={} WHERE pid={};").format(
            sql.Literal(rid), sql.Literal(pid))
        appConfig.DB_CONN.execute_update_query(query)


def insert_new_pipeline(uid, cid, category, timestamp, deadline, rid):
    '''
    Insert new pipeline into pipelines table, returns pid
    '''
    query = sql.SQL("INSERT INTO pipelines(uid, cid, stage, timestamp, deadline, rid) \
            VALUES({}, {}, {}, {}, {}, {}) RETURNING pid;").format(
                sql.Literal(uid), sql.Literal(cid), sql.Literal(category),
                sql.Literal(timestamp), sql.Literal(deadline), sql.Literal(rid))
    return appConfig.DB_CONN.execute_insert_return_query(query)


def insert_todo(uid, pid, company, deadline, category):
    '''
    Insert todo when user progresses to certain stages
    '''
    category_to_todo = {
        'CODING_CHALLENGE': 'Complete coding challenge',
        'INTERVIEW': 'Prepare for interview',
        'OFFER': 'Review offer'
    }
    category = LABELS_TO_CATEGORIES[category]
    if category not in category_to_todo.keys():
        return
    task = category_to_todo[category]
    if is_far_away(deadline):
        deadline = 'epoch'

    query = sql.SQL("INSERT INTO todos(uid, company, deadline, task, pid) \
        VALUES ({}, {}, {}, {}, {})").format(sql.Literal(uid), sql.Literal(company),
                                             sql.Literal(deadline), sql.Literal(task),
                                             sql.Literal(pid))
    appConfig.DB_CONN.execute_insert_query(query)


def is_far_away(deadline):
    '''
    Determines if a deadline is too far out to insert into todos
    '''
    if deadline == 'epoch':
        return False
    threshold_days = 90
    today = datetime.utcnow().replace(tzinfo=pytz.utc)
    return (deadline - today).days > threshold_days


def insert_into_insights(uid, cid, category, timestamp):
    '''
    Inserts new row into data insights table
    '''
    years_to_graduate = calc_years_to_graduate(uid)

    if years_to_graduate < 0:
        return

    stages = ['APPLICATION_CONF', 'REFERRAL', 'CODING_CHALLENGE', 'INTERVIEW', 'OFFER', 'REJECTION']
    if LABELS_TO_CATEGORIES[category] in stages:
        query = sql.SQL("INSERT INTO stages (uid, cid, stage, timestamp, years_to_graduate) \
            VALUES ({}, {}, {}, {}, {})").format(sql.Literal(uid), sql.Literal(cid),
                                                 sql.Literal(category), sql.Literal(timestamp),
                                                 sql.Literal(years_to_graduate))
        appConfig.DB_CONN.execute_insert_query(query)


def update_insights(uid, cid, timestamp, category, current_stage):
    """
    Updates data insights table based on given email categorization.
    """
    years_to_graduate = calc_years_to_graduate(uid)

    if years_to_graduate < 0:
        return

    query = sql.SQL("SELECT * FROM stages WHERE uid={} AND cid={} AND stage={} \
        AND years_to_graduate ={}").format(sql.Literal(uid), sql.Literal(cid),
                                           sql.Literal(category), sql.Literal(years_to_graduate))
    db_res = appConfig.DB_CONN.execute_select_query(query)

    if db_res != []:
        return

    insert_into_insights(uid, cid, category, timestamp)

    stages = ['APPLICATION_CONF', 'REFERRAL', 'CODING_CHALLENGE', 'INTERVIEW']
    stages_to_ignore = ['POST_OFFER']
    if compare_stages(current_stage, category) and LABELS_TO_CATEGORIES[current_stage] in stages \
            and LABELS_TO_CATEGORIES[category] not in stages_to_ignore:

        query = sql.SQL("SELECT timestamp, sid FROM stages WHERE uid={} AND cid={} AND stage={} \
            AND years_to_graduate={}").format(sql.Literal(uid), sql.Literal(cid),
                                              sql.Literal(current_stage),
                                              sql.Literal(years_to_graduate))
        response = appConfig.DB_CONN.execute_select_query(query)

        if response == []:
            print("ERROR: unable to update insights")
            return
        old_timestamp, sid = response[0][0], response[0][1]

        duration = calc_duration(old_timestamp, timestamp)

        update_query = sql.SQL("UPDATE stages SET duration={} WHERE sid={}").format(
            sql.Literal(duration), sql.Literal(sid))
        _temp = appConfig.DB_CONN.execute_update_query(update_query)


def compare_stages(current_stage, new_stage):
    '''
    Compares two stages and returns whether new_stage > current_stage
    '''
    ordering = {
        'TODO': 0,
        'PRE_APP': 1,
        'APPLICATION_CONF': 2,
        'REFERRAL': 3,
        'CODING_CHALLENGE': 4,
        'INTERVIEW': 5,
        'OFFER': 6,
        'REJECTION': 7,
        'POST_OFFER': 8
    }
    current_stage, new_stage = LABELS_TO_CATEGORIES[current_stage], LABELS_TO_CATEGORIES[new_stage]
    return ordering[new_stage] > ordering[current_stage]


def calc_years_to_graduate(uid):
    '''
    Calculates years_to_graduate
    '2022 recruiting in Jan 2020 => 2, '2022 recruiting in Sep 2020 => 1
    '''
    query = sql.SQL("SELECT year FROM users WHERE uid={}").format(sql.Literal(uid))
    db_res = appConfig.DB_CONN.execute_select_query(query)
    try:
        year = db_res[0][0]
        current_year, current_month = datetime.utcnow().year, datetime.utcnow().month
        offset = 1 if current_month > 5 else 0
        res = year - current_year - offset
    except Exception as e:
        print(e, "ERROR: Cannot calculate years to graduation for uid {}".format(uid))
        res = -1
    return res


def calc_duration(old_timestamp, timestamp):
    '''
    Calculates duration between two stages
    '''
    if isinstance(old_timestamp, str):
        old_timestamp = datetime.strptime(old_timestamp, '%Y-%m-%d %H:%M:%S')
    if isinstance(timestamp, str):
        timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    return (timestamp - old_timestamp).days


def update_link(email_resp, pid, stage):
    '''
    Update pipeline entry with coding challenge link, or set link to NULL otherwise
    '''
    if stage != CATEGORIES_TO_LABELS['CODING_CHALLENGE'] or 'challenge_link' not in email_resp:
        query = sql.SQL("UPDATE pipelines SET link=NULL WHERE pid={}").format(sql.Literal(pid))
        appConfig.DB_CONN.execute_update_query(query)
        return

    link = email_resp['challenge_link']
    if link is not None:
        query = sql.SQL("UPDATE pipelines SET link={} WHERE pid={}").format(
            sql.Literal(link), sql.Literal(pid))
        appConfig.DB_CONN.execute_update_query(query)
