'''
Facilitates todo table changes from front-end

Routes:
pursu.dev/api/todo/add ==> add todo to user's dashboard
pursu.dev/api/todo/delete ==> delete todo from user's dashboard
pursu.dev/api/todo/update ==> update todo on user's dashboard
'''

# pylint: disable=E1101
import datetime
from flask import request, jsonify, abort
from psycopg2 import sql

from api import app, add_to_state, appConfig
from api.utils import user_exists

@app.route('/api/todo/add', methods=['POST'])
def add_todo_item():
    '''
    Route: /api/todo/add
    Description: Dashboard API route to add a new todo item to user's dashboard
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
        add_to_state(email, body)
        if body['task'] == "":
            abort(400, "Empty task sent:", body["task"])

        created = datetime.datetime.utcnow()
        sql_query = sql.SQL("INSERT INTO todos(uid, task, created) VALUES({}, {}, {})").format(
            sql.Literal(uid), sql.Literal(body['task']), sql.Literal(created))
        appConfig.DB_CONN.execute_insert_query(sql_query)

        sql_query = sql.SQL("SELECT tid FROM todos WHERE uid={} AND created={}").format(
            sql.Literal(uid), sql.Literal(created))

        db_res = appConfig.DB_CONN.execute_select_query(sql_query)
        if db_res == []:
            abort(400, "ERROR: Todo insertion failed")
        tid = db_res[0][0]
        context["tid"] = tid

        if body['company'] != "":
            sql_query = sql.SQL("UPDATE todos SET company={} WHERE tid={}").format(
                sql.Literal(body['company']), sql.Literal(tid))
            appConfig.DB_CONN.execute_update_query(sql_query)

        if body['deadline'] != "":
            sql_query = sql.SQL("UPDATE todos SET deadline={} WHERE tid={}").format(
                sql.Literal(body['deadline']), sql.Literal(tid))
            appConfig.DB_CONN.execute_update_query(sql_query)
        return jsonify(**context), 200
    return jsonify(**context), 400


@app.route('/api/todo/delete', methods=['POST'])
def delete_todo_item():
    '''
    Route: /api/todo/delete
    Description: Dashboard API route to delete todo item
    '''
    body = request.get_json()
    token = body['token']
    context = {'token': token}

    query = sql.SQL("SELECT uid, email FROM gmail WHERE token={}").format(sql.Literal(token))
    res = appConfig.DB_CONN.execute_select_query(query)

    if res == []:
        abort(400, "Invalid token")
    uid, email = res[0][0], res[0][1]

    if all([True for arg in [uid, email] if arg]) and user_exists(email):
        add_to_state(email, body)
        if body['tid'] == "":
            abort(400, "Empty tid sent:", body["tid"])
        # check that the todo belongs to the respective user
        sql_query = sql.SQL("SELECT uid FROM todos WHERE tid={}").format(sql.Literal(body['tid']))

        db_res = appConfig.DB_CONN.execute_select_query(sql_query)
        if db_res == []:
            abort(400, "ERROR: uid does not exist for tid={}".format(body['tid']))
        todo_uid = db_res[0][0]

        if int(todo_uid) != int(uid):
            abort(400, "tid does not belong to respective user")
        sql_query = sql.SQL("DELETE FROM todos WHERE tid={}").format(sql.Literal(body['tid']))
        appConfig.DB_CONN.execute_delete_query(sql_query)
        return jsonify(**context), 200
    return jsonify(**context), 400


@app.route('/api/todo/update', methods=['POST'])
def update_todo_item():
    '''
    Route: /api/todo/update
    Description: Dashboard API route to update todo item
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
        add_to_state(email, body)
        if body['tid'] == "":
            abort(400, "Empty tid sent:", body["tid"])
        # check that the todo belongs to the respective user
        sql_query = sql.SQL("SELECT uid FROM todos WHERE tid={}").format(sql.Literal(body['tid']))

        db_res = appConfig.DB_CONN.execute_select_query(sql_query)
        if db_res == []:
            abort(400, "ERROR: uid does not exist for tid={}".format(body['tid']))

        todo_uid = db_res[0][0]
        if int(todo_uid) != int(uid):
            abort(400, "tid does not belong to respective user")

        queries = []
        sql_query = sql.SQL("UPDATE todos SET company={} WHERE tid={}").format(
            sql.Literal(body['company']), sql.Literal(body['tid']))
        queries.append(sql_query)
        sql_query = sql.SQL("UPDATE todos SET deadline={} WHERE tid={}").format(
            sql.Literal(body['deadline']), sql.Literal(body['tid']))
        queries.append(sql_query)
        sql_query = sql.SQL("UPDATE todos SET task={} WHERE tid={}").format(
            sql.Literal(body['task']), sql.Literal(body['tid']))
        queries.append(sql_query)

        for query in queries:
            appConfig.DB_CONN.execute_update_query(query)

        return jsonify(**context), 200
    return jsonify(**context), 400
