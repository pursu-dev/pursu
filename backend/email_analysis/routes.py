'''
Facilitates email analysis and all communication with gmail pub/sub push notifications

Routes:
pursu.dev/api/email_analysis/health ==> health check for email analysis pipeline
pursu.dev/api/email_analysis/new_message ==> receive push notification for new email and analyze
'''
# pylint: disable=E1101,W0612,W0613

import json
import base64
import re
import threading
import traceback
from flask import request
from apiclient import discovery, errors
from psycopg2 import sql
from email_analysis import app, limiter, add_to_state
from email_analysis import appConfig, scrape_email, get_credentials
from email_analysis.parse_info import get_email_information
from email_analysis import sagemaker_client
from email_analysis import filters, data_utils
from email_analysis.pipeline_logic import update_pipeline

TOKEN_URI = 'https://oauth2.googleapis.com/token'


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


@app.route('/api/email_analysis/health', methods=["GET"])
def health_check():
    '''
    Route: /api/email_analysis/health
    Description: Health Check API Route for AWS Target Checks
    '''
    return 'OK'


@app.route('/api/email_analysis/new_message', methods=['GET', 'POST'])
@limiter.limit("10 per second")
def get_message():
    '''
    Route: /api/email_analysis/new_message
    Description: Push notification API route for communication with pub/sub when new email arrives
    '''
    if request.method == 'POST':
        print('serving pubsub request')
        data = request.data.decode('utf-8')
        payload = json.loads(data)

        if 'message' not in payload or 'data' not in payload['message']:
            print('Malformed pubsub notification')
            return 'OK', 200

        message = base64.b64decode(payload['message']['data'])
        message = json.loads(message.decode('utf-8'))

        # Check for start_watching response in topic
        if 'emailAddress' not in message:
            print("Different Mailbox {}".format(message))
            return 'OK', 200

        # grab previous history id
        email = message['emailAddress']
        add_to_state(email)
        new_history_id = message['historyId']
        sql_query = sql.SQL("SELECT history FROM gmail WHERE email={}").format(sql.Literal(email))
        temp = appConfig.DB_CONN.execute_select_query(sql_query)

        if temp == []:
            print('Empty history ID for account {}'.format(email.strip().rstrip()))
            return 'OK', 200

        previous_history_id = temp[0][0]
        sql_query = sql.SQL("UPDATE gmail SET history={} WHERE email={}").format(
            sql.Literal(new_history_id), sql.Literal(email))
        _updated_rows = appConfig.DB_CONN.execute_update_query(sql_query)

        scraped_email, email_out = get_email(email, previous_history_id)
        if scraped_email is not None and email_out is not None:
            categorize_and_update_pipeline(scraped_email, email_out, email)
    return 'OK', 200


def categorize_and_update_pipeline(email_df, raw_email_resp, user_email):
    '''
    Function that runs entire email analysis for a single parsed email
    '''
    if not filters.denylist_filter(appConfig, email_response=email_df):
        print("Email did not pass layer 2 filters\n")
        return
    category = run_models(email_df)
    parsed_email_info = get_email_information(
        resp=raw_email_resp,
        category=category,
        user_email=user_email
    )
    update_pipeline(parsed_email_info, category, user_email)
    write_email(email_df=email_df, user_email=user_email)


def write_email(email_df, user_email):
    '''
    Write email to S3 container after anonymization. Only writes if user gives consent
    '''
    query = sql.SQL("SELECT U.name, U.consent FROM users U, gmail G WHERE U.uid = G.uid \
        and G.email = {}").format(sql.Literal(user_email))
    db_res = appConfig.DB_CONN.execute_select_query(query)
    if db_res == []:
        print("ERROR: could not write email to S3 for user {}".format(user_email))
    name, consent = db_res[0]

    if consent == 1:
        anon_email = data_utils.anonymize_and_write_to_S3(email_df, name, user_email)
        add_to_state(anon_email)


def run_models(scraped_email):
    '''
    Access categorization model endpoints to get classification for email
    '''
    if 'subject' not in scraped_email or 'body' not in scraped_email:
        return -1

    email_text = scraped_email['subject'] + " " + scraped_email['body']
    email_text = re.sub(r',', '', email_text)

    response = sagemaker_client.invoke_endpoint(EndpointName='pursu-layer3',
                                                Body=email_text,
                                                ContentType='text/csv')

    relevance = int(response['Body'].read())
    if int(relevance) == 0:
        response = sagemaker_client.invoke_endpoint(
            EndpointName='pursu-layer4',
            Body=email_text,
            ContentType='text/csv',
        )
        return int(response['Body'].read())

    return -1


def get_email(email, history_id):
    '''
    Grab email content from user's account given historyID
    '''
    try:
        creds = get_credentials(email, appConfig)
        if creds is None:
            return None, None
        gmail = discovery.build('gmail', 'v1', credentials=creds)

        sql_query = sql.SQL("SELECT label FROM gmail WHERE email={}").format(sql.Literal(email))
        res = appConfig.DB_CONN.execute_select_query(sql_query)
        label_id = res[0][0] if res != [] else None

        out = gmail.users().history().list(
            userId='me',
            labelId=label_id,
            maxResults=1,
            startHistoryId=history_id,
            historyTypes='messageAdded').execute()

        if 'history' not in out:
            # No longer an error (we expect POST to come in pairs by virtue
            # of re-adding labels, and we will get a lot more notifications now)
            return None, None

        msg_id = out['history'][0]['messages'][0]['id']

        # Message is already unread/in Inbox
        email_out = gmail.users().messages().get(userId='me', id=msg_id).execute()

        # parse out for message body
        scraped = scrape_email.scrape_email_info(email_out)

        return scraped, email_out
    except errors.HttpError as error:
        print("EXCEPTION: {}".format(error))
        return None, None
