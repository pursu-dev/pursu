"""Email Analysis API pipeline"""

import os
import logging
from threading import get_ident
import flask
import psycopg2
import boto3
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from slacker_log_handler import SlackerLogHandler, NoStacktraceFormatter
from shared import config, data_utils, scrape_email, filters
from shared.config import get_config
from cron_jobs.jobs import get_credentials

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

sagemaker_client = boto3.client(
    'sagemaker-runtime',
    region_name='us-east-2',
    aws_access_key_id=appConfig.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=appConfig.AWS_SECRET_ACCESS_KEY)

app.state = {}

def add_to_state(*args):
    '''
    Function to add arguments to state. Used for more descriptive error messages
    '''
    app.state[get_ident()].extend(list(args))


LABELS_TO_CATEGORIES = {
    -1: 'IRRELEVANT',
    0: 'APPLICATION_CONF',
    1: 'REFERRAL',
    2: 'CODING_CHALLENGE',
    3: 'INTERVIEW',
    4: 'INTERVIEW',
    5: 'OFFER',
    6: 'REJECTION',
    7: 'IRRELEVANT',
    8: 'PRE_APP',
    9: 'POST_OFFER',
    10: 'TODO'
}

CATEGORIES_TO_LABELS = {
    'IRRELEVANT': -1,
    'APPLICATION_CONF': 0,
    'REFERRAL': 1,
    'CODING_CHALLENGE': 2,
    'INTERVIEW': 3,
    'OFFER': 5,
    'REJECTION': 6,
    'PRE_APP': 8,
    'POST_OFFER': 9,
    'TODO': 10
}


import email_analysis.routes  # noqa: E402,R0401  pylint: disable=wrong-import-position,R0401
