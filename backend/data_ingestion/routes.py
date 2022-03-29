'''
Facilitates all data collection efforts for model training data

Routes:
pursu.dev/api/data_ingestion/health ==> Health check
pursu.dev/api/data_ingestion/storeauthtraining ==> Obtain and write user email data
pursu.dev/api/data_ingestion/watch_cron_job ==> Renew or halt gmail watch for users
pursu.dev/api/data_ingestion/update_jobs ==> Cron job route for updating jobs table
pursu.dev/api/data_ingestion/update_stage_insights ==> Cron job route for updating stage insights
pursu.dev/api/data_ingestion/generate_trending_companies ==> Cron job for trending companies
'''
from threading import Thread

from flask import request, abort
from oauth2client import client
from psycopg2 import sql

from data_ingestion import app, appConfig
from data_ingestion import FlaskThread
from data_ingestion import stop_inactive_and_renew
from data_ingestion import trending_companies
from data_ingestion.collect_data import gather_training_data
from data_ingestion import JobListingUpdateManager, update_stage_durations, pipeline_updates


@app.route('/api/data_ingestion/health', methods=['GET'])
def health_check():
    '''
    Route: /api/data_ingestion/health
    Description: Health check for data ingestion api
    '''
    return 'OK'


@app.route('/api/data_ingestion/storeauthtraining', methods=['GET', 'POST'])
def store_auth_training():
    '''
    Route: /api/data_ingestion/storeauthtraining
    Description: Handle data grab for user from front-end request
    '''
    auth_code = request.json['token']

    # If this request does not have `X-Requested-With` header, this could be a CSRF
    if request.method == 'POST' and not request.headers.get('X-Requested-With'):
        abort(403, 'Malformed ')

    # Exchange auth code for access token, refresh token, and ID token
    google_creds = appConfig.GOOGLE_CLIENT_CREDENTIALS

    creds = client.credentials_from_code(google_creds["client_id"],
                                         google_creds["client_secret"],
                                         'https://www.googleapis.com/auth/gmail.readonly',
                                         auth_code)

    # Pass creds to function to collect data
    email = creds.id_token['email']

    # Check if user has already provided data
    sql_query = sql.SQL("SELECT * FROM data_providers WHERE email={}").format(sql.Literal(email))
    temp = appConfig.DB_CONN.execute_select_query(sql_query)

    if temp == []:
        ins_query = sql.SQL("INSERT INTO data_providers(email) VALUES({})").format(
            sql.Literal(email))
        appConfig.DB_CONN.execute_insert_query(ins_query)

        # Spin up a new thread to handle the request
        data_grab = Thread(target=gather_training_data, args=[email, creds])
        data_grab.start()

    return 'OK', 200


@app.route('/api/data_ingestion/watch_cron_job', methods=['GET'])
def run_watch_cron_job():
    '''
    Route: /api/data_ingestion/watch_cron_job
    Description: Cron job route to renew watch for all active users; halt for inactive users
    '''
    FlaskThread(target=stop_inactive_and_renew, args=[appConfig, app]).start()
    return 'OK', 200

@app.route('/api/data_ingestion/generate_trending_companies', methods=['GET'])
def run_generate_trending_companies():
    '''
    Route: /api/data_ingestion/generate_trending_companies
    Description: Route for generating weekly trending companies
    '''
    trending_companies.generate_trends(appConfig)
    return 'OK', 200

@app.route('/api/data_ingestion/update_jobs', methods=['GET'])
def run_update_jobs_cron_job():
    '''
    Route: /api/data_ingestion/update_jobs
    Description: Cron job route for updating jobs table
    '''
    job_listing_update_manager = JobListingUpdateManager(appConfig)
    job_listing_update_manager.update_jobs()
    return 'OK', 200

@app.route('/api/data_ingestion/update_stage_insights', methods=['GET'])
def update_insights_cron_job():
    '''
    Route: /api/data_ingestion/update_stage_insights
    Description: Cron job route for updating stage insights data
    '''
    pipeline_updates.update_pipelines(appConfig)
    update_stage_durations.update_stage_durations(appConfig)
    return 'OK', 200
