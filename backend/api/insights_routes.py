'''
Facilitates insights delivery

Routes:
pursu.dev/api/insights/collaborative_recommendations ==> insight #2
'''
# pylint: disable=R1718,C0301
from json import dumps
from flask import request, abort, jsonify
import boto3
from psycopg2 import sql

from api import app, appConfig
from api.utils import user_exists

STAGE_INSIGHTS_QUERY = 'SELECT stage, duration, min_date, max_date FROM stage_durations WHERE cid={}'
REDEEMED_RECRUITERS_QUERY = "SELECT RR.rid from redeemed_recruiters RR INNER JOIN gmail G \
                              USING(uid) INNER JOIN recruiters R USING(rid) INNER JOIN companies C \
                                  using(cid) WHERE G.token = {} AND C.cid = {}"
RECRUITERS_QUERY = "SELECT R.rid from recruiters R INNER JOIN companies C USING(cid) WHERE C.cid={}"
VALID_TOKEN_QUERY = "SELECT G.uid FROM gmail G WHERE G.token={}"

@app.route('/api/insights/collaborative_recommendations', methods=['POST'])
def collaborative_recommendations():
    '''
    Route: /api/insights/collaborative_recommendations
    Description: Returns top 5 company recommendations by querying AWS personalize endpoint
    '''
    body = request.get_json()
    token = body['token']
    context = {'token': token}

    query = sql.SQL("SELECT uid, email FROM gmail WHERE token={}").format(sql.Literal(token))
    res = appConfig.DB_CONN.execute_select_query(query)

    if res == []:
        abort(400, 'Invalid token')
    uid, email = res[0][0], res[0][1]

    if all([True for arg in [uid, email] if arg]) and user_exists(email):
        personalizeRt = boto3.client('personalize-runtime',
                                     region_name='us-east-2',
                                     aws_access_key_id=appConfig.AWS_ACCESS_KEY_ID,
                                     aws_secret_access_key=appConfig.AWS_SECRET_ACCESS_KEY)
        response = personalizeRt.get_recommendations(campaignArn=appConfig.CAMPAIGN_ARN,
                                                     userId=str(uid))
        recs = set([int(i['itemId']) for i in response['itemList']])

        query = sql.SQL("SELECT cid FROM pipelines WHERE uid={}").format(sql.Literal(uid))
        res = appConfig.DB_CONN.execute_select_query(query)
        companies = set([i[0] for i in res])
        recommendations = recs - companies
        context['recommendations'] = list(recommendations)[:5]
        return jsonify(**context), 200
    return jsonify(**context), 400


@app.route('/api/insights/get_stage_insights', methods=['POST'])
def get_stage_insights():
    '''
    Route: /api/insights/get_stage_insights
    Description: Returns average stage durations
    '''
    body = request.get_json()
    cid = body.get('cid')
    token = body.get('token')

    if cid is not None and token is not None and validate_token(token):
        sql_query = sql.SQL(STAGE_INSIGHTS_QUERY).format(sql.Literal(cid))
        query_result = appConfig.DB_CONN.execute_select_query(sql_query)
        return dumps(query_result, default=str), 200
    return dumps("Invalid arguments"), 400

@app.route('/api/insights/get_redeemed_recruiter_data', methods=['POST'])
def get_recruiter_data():
    '''
    Route: /api/insights/get_redeemed_recruiter_data
    Description: Returns recruiter data
    '''
    body = request.get_json()
    cid = body.get('cid')
    token = body.get('token')
    if cid is not None and token is not None:
        recruiters_sql = sql.SQL(RECRUITERS_QUERY).format(sql.Literal(cid))
        recruiters_result = appConfig.DB_CONN.execute_select_query(recruiters_sql)
        redeemed_sql = sql.SQL(REDEEMED_RECRUITERS_QUERY).format(sql.Literal(token),
                                                                 sql.Literal(cid))
        redeemed_result = appConfig.DB_CONN.execute_select_query(redeemed_sql)
        if len(redeemed_result) == len(recruiters_result):
            return "false", 200
        return "true", 200
    return dumps("Invalid arguments"), 400

def validate_token(token):
    '''Given a token, determines if this an active user in the db.'''
    valid_token_sql = sql.SQL(VALID_TOKEN_QUERY).format(sql.Literal(token))
    uid_result = appConfig.DB_CONN.execute_select_query(valid_token_sql)
    return uid_result != []
