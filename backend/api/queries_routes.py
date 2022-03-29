'''
Run queries for front-end

Routes:
pursu.dev/api/queries ==> run query
'''

# pylint: disable=E1101,C0301
from json import dumps
from flask import request
from psycopg2 import sql

from api import app, appConfig, limiter

MASTER_QUERIES = {
    "user_info": "SELECT U.uid, name, college, major, year, gender, ethnicity, email, R.points FROM Users U INNER JOIN Gmail G ON U.uid = G.uid LEFT JOIN Referrals R ON R.uid = U.uid WHERE G.token = {} ",
    "pipeline_uid": "SELECT login, pid, C.cid, timestamp, stage, R.name, R.email, link, notes, deadline, P.active, C.name, G.email, G.uid FROM Gmail G INNER JOIN Users U USING(uid) INNER JOIN Pipelines P USING(uid) INNER JOIN Companies C USING(cid) LEFT JOIN Recruiters R USING(rid) WHERE G.token = {}",
    "todo": "SELECT T.tid, T.company, T.deadline, T.task, P.link FROM Gmail G INNER JOIN Users U USING(uid) INNER JOIN Todos T USING(uid) LEFT JOIN pipelines P USING(pid) WHERE token = {}",
    "companies": "SELECT cid, name, logo FROM companies as C WHERE C.user_created = 0 ORDER BY name ASC",
    "bugs": "SELECT bug FROM bugs ORDER BY created DESC",
    "explore": "SELECT C.cid, T.cid AS trending, C.name, C.logo, J.link, J.location, J.internship, J.timestamp, CASE WHEN EXISTS (SELECT * FROM stage_durations WHERE cid=C.cid) THEN TRUE ELSE FALSE END FROM companies C LEFT JOIN trending_companies T USING(cid) LEFT JOIN jobs J USING(cid) WHERE C.cid in (SELECT cid FROM stage_durations UNION SELECT cid FROM jobs) AND J.approved IS NOT FALSE AND C.user_created != 1",
    "redeemed_recruiters": "SELECT R.name, R.email from redeemed_recruiters RR INNER JOIN gmail G USING(uid) INNER JOIN recruiters R USING(rid) WHERE G.token = {} AND R.cid = {}",
    "similar_companies": "SELECT name, sector, logo FROM company_suggestions JOIN companies ON cid2=cid WHERE cid1={} ORDER BY ord ASC LIMIT 3"
}

QUERIES_WITHOUT_ARGUMENTS = ['companies', 'bugs', 'explore']
QUERIES_WITH_CID = ['similar_companies']
QUERIES_WITH_CID_AND_TOKEN = ['redeemed_recruiters']


@app.route('/api/queries', methods=['POST'])
@limiter.exempt
def run_query():
    '''
    Route: /api/queries
    Description: Query API
    '''
    body = request.get_json()
    query_name = body.get('query_name')
    query_token = body.get('token')
    query_cid = body.get('cid')

    if is_user_valid(query_token) and query_name in MASTER_QUERIES.keys():
        if query_name in QUERIES_WITHOUT_ARGUMENTS:
            sql_query = sql.SQL(MASTER_QUERIES[query_name])
        elif query_name in QUERIES_WITH_CID:
            sql_query = sql.SQL(
                MASTER_QUERIES[query_name]).format(sql.Literal(query_cid))
        elif query_name in QUERIES_WITH_CID_AND_TOKEN:
            sql_query = sql.SQL(
                MASTER_QUERIES[query_name]).format(
                    sql.Literal(query_token),
                    sql.Literal(query_cid))
        else:
            sql_query = sql.SQL(MASTER_QUERIES[query_name]).format(sql.Literal(query_token))

        query_result = appConfig.DB_CONN.execute_select_query(sql_query)
        return dumps(query_result, default=str), 200
    return dumps("Invalid query name"), 400


def is_user_valid(token):
    '''
    Function to verify that valid token is given
    '''
    if token is None:
        return False

    sql_query = sql.SQL("SELECT COUNT(*) FROM gmail WHERE token={}").format(sql.Literal(token))
    query_result = appConfig.DB_CONN.execute_select_query(sql_query)[0][0]
    return query_result == 1
