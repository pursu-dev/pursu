'''
Facilitates user account sign-up/login
Facilitates dashboard changes from front-end
Facilitates recruiter changes from front-end
Facilitates todo changes from front-end
Facilitates beta user account verification
'''

# pylint: disable=E1101,W0612,W0613,W0611
import threading
import traceback
from flask import request
from api import app, appConfig


@app.before_request
def before_request_func():
    '''
    Creates thread key in state dict
    '''
    app.state[threading.get_ident()] = [request.path]


@app.teardown_request
def teardown_request_func(error=False):
    '''
    Deletes thread key from state dict
    '''
    del app.state[threading.get_ident()]


@app.errorhandler(Exception)
def handle_exception(e):
    '''
    Function to catch all exceptions and log to Slack
    '''
    for arg in app.state[threading.get_ident()]:
        e.args += (str(arg),)

    e.args += (str(traceback.format_exc()),)

    code = e.code if hasattr(e, 'code') else 500
    if code != 404:
        app.logger.error(e)
    return "BAD", code


@app.route('/api/health', methods=['GET'])
def health_check():
    '''
    Route: /api/health
    Description: Health Check API Route for AWS Target Checks
    '''
    return "OK", 200


import api.user_routes  # noqa: E402,R0401,W0611  pylint: disable=wrong-import-position,R0401,W0611
import api.recruiter_routes  # noqa: E402,R0401,W0611  pylint: disable=wrong-import-position,R0401,W0611
import api.dashboard_routes  # noqa: E402,R0401,W0611  pylint: disable=wrong-import-position,R0401,W0611
import api.beta_routes  # noqa: E402,R0401,W0611  pylint: disable=wrong-import-position,R0401,W0611
import api.todo_routes  # noqa: E402,R0401,W0611  pylint: disable=wrong-import-position,R0401,W0611
import api.insights_routes  # noqa: E402,R0401,W0611  pylint: disable=wrong-import-position,R0401,W0611
import api.queries_routes  # noqa: E402,R0401,W0611  pylint: disable=wrong-import-position,R0401,W0611
