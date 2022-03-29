"""Back end API"""
import sys
import os
from threading import Thread, get_ident

import flask
import psycopg2
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from shared import config, data_utils, filters, scrape_email
from shared.config import get_config
from cron_jobs.jobs import get_credentials, start_watching, stop_watching, create_creds

# initialize flask application
app = flask.Flask(__name__)

appConfig = get_config(app)

# rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["3 per second"],
    enabled=appConfig.RATE_LIMITING_ENABLED
)

app.state = {}

def add_to_state(*args):
    '''
    Function to add arguments to state. Used for more descriptive error messages
    '''
    app.state[get_ident()].extend(list(args))

import api.routes  # noqa: E402,R0401  pylint: disable=wrong-import-position,R0401
