'''
Routes for beta release; handle beta user permissions

Routes:
pursu.dev/api/beta/feedback ==> add feedback from beta users
'''

# pylint: disable=E1101
from flask import request
from psycopg2 import sql

from api import app, appConfig
from api.utils import user_exists

@app.route('/api/beta/feedback', methods=['POST'])
def add_beta_feedback():
    '''
    Route: /api/beta/feedback
    Description: Beta development API route to glean feedback from users
    '''
    body = request.get_json()

    if body['email'] != "" and body['comment'] != "" and user_exists(body['email']):
        comment = body['comment']
        sql_query = sql.SQL("INSERT INTO feedback(email, comment) VALUES({}, {})").format(
            sql.Literal(body['email']), sql.Literal(comment))
        appConfig.DB_CONN.execute_insert_query(sql_query)
        return 'OK', 200
    return 'BAD', 400
