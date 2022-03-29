'''
Facilitates dashboard changes from front-end

Routes:
pursu.dev/api/dashboard/edit ==> edit specific pipeline in user dashboard
pursu.dev/api/dashboard/add ==> add pipeline to dashboard
pursu.dev/api/dashboard/delete ==> delete pipeline from dashboard
pursu.dev/api/dashboard/deactivate ==> deactivate pipeline from user's dashboard
'''

# pylint: disable=E1101
from threading import Thread
from flask import request, jsonify, abort
from psycopg2 import sql

from api import app, filters, add_to_state, appConfig
from api.utils import user_exists, update_user_filters

@app.route('/api/dashboard/edit', methods=['POST'])
def edit_user_dashboard_info():
    '''
    Route: /api/dashboard/edit
    Description: Dashboard API route to edit pipeline state
    '''
    body = request.get_json()
    token = body['token']
    pid = body['pid']

    query = sql.SQL("SELECT email,uid FROM gmail WHERE token={}").format(sql.Literal(token))
    email, uid = appConfig.DB_CONN.execute_select_query(query)[0]

    context = {'email': email, 'pid': pid}
    if all([True for arg in [pid, email] if arg]) and user_exists(email):
        add_to_state(email, body)
        check_pipeline_constraints(pid, uid)
        queries = []
        status_code = 200
        if "company" in body:
            select_query = sql.SQL("SELECT cid FROM companies WHERE name={}").format(
                sql.Literal(body['company']))
            db_res = appConfig.DB_CONN.execute_select_query(select_query)
            if db_res == []:
                # If company doesn't exist, then add as a user-generated company
                cid = enter_new_company(company_name=body['company'])
                status_code = 201
            else:
                cid = db_res[0][0]
            update_query = sql.SQL("UPDATE pipelines SET cid={} WHERE pid={}").format(
                sql.Literal(cid), sql.Literal(pid))
            queries.append(update_query)
        if "stage" in body:
            update_query = sql.SQL("UPDATE pipelines SET stage={} WHERE pid={}").format(
                sql.Literal(body['stage']), sql.Literal(pid))
            queries.append(update_query)
        if "deadline" in body:
            update_query = sql.SQL("UPDATE pipelines SET deadline={} WHERE pid={}").format(
                sql.Literal(body['deadline']), sql.Literal(pid))
            queries.append(update_query)
        if "notes" in body:
            update_query = sql.SQL("UPDATE pipelines SET notes={} WHERE pid={}").format(
                sql.Literal(body['notes']), sql.Literal(pid))
            queries.append(update_query)

        for query in queries:
            appConfig.DB_CONN.execute_update_query(query)

        return jsonify(**context), status_code
    return jsonify(**context), 400


@app.route('/api/dashboard/add', methods=['POST'])
def add_user_dashboard_info():
    '''
    Route: /api/dashboard/add
    Description: Dashboard API route to add a new pipeline to user's dashboard
    '''
    body = request.get_json()
    token = body['token']
    uid = body['uid']
    stage = body['stage']
    company_name = body['company_name']
    notes = body['notes'] if "notes" in body else ""

    query = sql.SQL("SELECT email FROM gmail WHERE token={}").format(sql.Literal(token))
    email = appConfig.DB_CONN.execute_select_query(query)[0][0]

    context = {'uid': uid}
    for key in body:
        if not body[key]:
            body[key] = "NULL"

    if all([True for arg in [uid, email, stage, company_name] if arg
            ]) and user_exists(email):
        add_to_state(body)
        status_code = 200
        select_query = sql.SQL("SELECT cid FROM companies WHERE UPPER(name)=UPPER({})").format(
            sql.Literal(company_name))
        res = appConfig.DB_CONN.execute_select_query(select_query)

        if res == []:
            # If company doesn't exist, then add as a user-generated company
            cid = enter_new_company(company_name=company_name)
            status_code = 201
        else:
            cid = res[0][0]
            # Spin up a new thread to recompute filters for current user if necessary
            filter_thread = Thread(target=add_company_to_user_filters, args=[cid, email])
            filter_thread.start()

        sql_query = sql.SQL("INSERT INTO pipelines(cid, stage, uid, notes) \
            VALUES({}, {}, {}, {})").format(
                sql.Literal(cid), sql.Literal(stage), sql.Literal(uid), sql.Literal(notes))
        appConfig.DB_CONN.execute_insert_query(sql_query)
        pid = get_active_pid(uid, cid)
        context["pid"] = pid
        return jsonify(**context), status_code
    return jsonify(**context), 400


@app.route('/api/dashboard/delete', methods=['POST'])
def delete_user_dashboard_info():
    '''
    Route: /api/dashboard/delete
    Description: Dashboard API route to delete pipeline from user dashboard
    '''
    body = request.get_json()
    token = body['token']
    pid = body['pid']

    query = sql.SQL("SELECT email, uid FROM gmail WHERE token={}").format(sql.Literal(token))
    email, uid = appConfig.DB_CONN.execute_select_query(query)[0]

    context = {'email': email, 'pid': pid}
    if all([True for arg in [pid, email] if arg]) and user_exists(email):
        add_to_state(email, pid)
        check_pipeline_constraints(pid, uid)
        delete_query = sql.SQL("DELETE FROM pipelines WHERE pid={}").format(sql.Literal(pid))
        appConfig.DB_CONN.execute_delete_query(delete_query)
        return jsonify(**context), 200
    return jsonify(**context), 400


@app.route('/api/dashboard/deactivate', methods=['POST'])
def deactivate_pipeline():
    '''
    Route: /api/dashboard/deactivate
    Description: Dashboard API route to deactive a given pipeline
    '''
    body = request.get_json()
    pid = body['pid']
    email = body['email']
    context = {'email': email, 'pid': pid}
    if user_exists(email):
        add_to_state(body)
        sql_query = sql.SQL("UPDATE pipelines SET active={} WHERE pid={}").format(
            sql.Literal(int(False)), sql.Literal(pid))
        appConfig.DB_CONN.execute_update_query(sql_query)
        return jsonify(**context), 200
    return jsonify(**context), 400


def enter_new_company(company_name, user_created=True):
    '''
    Enter new company name into database.
    User-created companies are not tracked by Pursu email analysis,
    but can be manually updated
    '''
    sql_query = sql.SQL("INSERT INTO companies(name, user_created) VALUES ({}, {}) \
        RETURNING cid;").format(sql.Literal(company_name), sql.Literal(int(user_created)))

    cid = appConfig.DB_CONN.execute_insert_return_query(sql_query)

    # Create new filters (Not updating for all users)
    if not user_created:
        _, version = filters.create_filters(appConfig)

        # Update company filter version
        sql_query = sql.SQL("UPDATE companies SET filt_version={} WHERE name={}").format(
            sql.Literal(version), sql.Literal(company_name))
        appConfig.DB_CONN.execute_update_query(sql_query)
    return cid


def add_company_to_user_filters(cid, user_email):
    '''
    Edit the current user's filters to include the new company
    '''
    sql_query = sql.SQL("SELECT uid, label FROM gmail WHERE email={}").format(
        sql.Literal(user_email))
    db_res = appConfig.DB_CONN.execute_select_query(sql_query)
    if db_res == []:
        print("ERROR: Cannot find uid or label for user email {}".format(user_email))
    uid, label_id = db_res[0]

    if user_requires_filter_update(uid=uid, cid=cid):
        update_user_filters(email=user_email, label_id=label_id)


def user_requires_filter_update(uid, cid):
    '''
    Function to determine if user requires filter update.
    '''
    sql_query = sql.SQL("SELECT filt_version FROM users WHERE uid={}").format(sql.Literal(uid))
    db_res = appConfig.DB_CONN.execute_select_query(sql_query)
    if db_res == []:
        print("ERROR: no filt_version for uid={}".format(uid))
        return False
    user_version = db_res[0][0]

    sql_query = sql.SQL("SELECT filt_version FROM companies WHERE cid={}").format(sql.Literal(cid))
    db_res = appConfig.DB_CONN.execute_select_query(sql_query)
    if db_res == []:
        print("ERROR: no filt_version for cid={}".format(cid))
        return False
    comp_version = db_res[0][0]

    if user_version >= comp_version:
        return False
    return True


def get_active_pid(uid, cid):
    '''
    Function to return pid of active pipeline
    '''
    sql_query = sql.SQL("SELECT pid FROM pipelines WHERE uid={} AND cid={} AND active=1").format(
        sql.Literal(uid), sql.Literal(cid))
    db_res = appConfig.DB_CONN.execute_select_query(sql_query)
    return db_res[0][0] if db_res != [] else None


def check_pipeline_constraints(pid, uid):
    '''
    Function to ensure that a pipeline request belongs to right user
    '''
    sql_query = sql.SQL("SELECT uid FROM pipelines WHERE pid={}").format(sql.Literal(pid))
    db_res = appConfig.DB_CONN.execute_select_query(sql_query)

    if db_res == []:
        abort(400, "ERROR: uid does not exist for pid={}".format(pid))
    pipeline_uid = db_res[0][0]

    if int(pipeline_uid) != int(uid):
        abort(400, "pid does not belong to respective user")
