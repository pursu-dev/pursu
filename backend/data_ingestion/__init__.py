"""Data Ingestion API pipeline"""

import os
import logging
from threading import Thread
import flask
import psycopg2

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from slacker_log_handler import SlackerLogHandler, NoStacktraceFormatter

from cron_jobs.jobs import stop_inactive_and_renew
from cron_jobs.update_jobs import JobListingUpdateManager
from insights import pipeline_updates, update_stage_durations, trending_companies
from shared import data_utils, scrape_email, filters
from shared import config
from shared.config import get_config

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


class FlaskThread(Thread):
    '''
    Wrapper to run thread within app context
    '''

    def __init__(self, *args, **kwargs):
        '''
        Initialize thread
        '''
        super().__init__(*args, **kwargs)
        self.app = app

    def run(self):
        '''
        Override run function
        '''
        with self.app.app_context():
            super().run()


import data_ingestion.routes  # noqa: E402,R0401  pylint: disable=wrong-import-position,R0401
