'''
Facilitates recruiter changes from front-end

Routes:
pursu.dev/api/recruiter/add ==> add recruiter to database
pursu.dev/api/recruiter/edit ==> edit recruiter information in database (NOT IMPLEMENTED)
'''

# pylint: disable=E1101
from flask import request, jsonify, abort
from psycopg2 import sql

from api import app, appConfig

@app.route('/api/recruiter/add', methods=['POST'])
def add_recruiter_info():
    '''
    Route: /api/recruiter/add
    Description: Recruiter API route to add new recruiter to database
    '''
    body = request.get_json()
    company_name = body['company_name']
    recruiter_email = body['email']
    recruiter_name = body['name']

    context = {'company': company_name, 'email': recruiter_email}
    for key in body.keys():
        if not body[key]:
            body[key] = "NULL"
    if all([True for arg in [company_name, recruiter_email] if arg]):
        select_query = sql.SQL("SELECT cid FROM companies WHERE name={}").format(
            sql.Literal(company_name))
        db_res = appConfig.DB_CONN.execute_select_query(select_query)
        if db_res == []:
            abort(400, "ERROR: cid not found for company: {}".format(company_name))
        cid = db_res[0][0]
        sql_query = sql.SQL("INSERT INTO recruiters(cid, name, email) VALUES ({}, {}, {})").format(
            sql.Literal(cid), sql.Literal(recruiter_name), sql.Literal(recruiter_email))
        appConfig.DB_CONN.execute_insert_query(sql_query)
        return jsonify(**context), 200
    return jsonify(**context), 400

# TODO: discuss logic for globally editing recruiter info
# @app.route('/api/recruiter/edit', method=['POST'])
# def edit_recruiter_info():
