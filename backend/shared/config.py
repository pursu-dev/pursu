'''
Configuration Data
'''
# pylint: disable=R0902
from email.utils import formataddr
from email.header import Header
from email.mime.text import MIMEText
import smtplib
import logging
import os
import boto3
from psycopg2 import sql
from cryptography.fernet import Fernet
from slacker_log_handler import SlackerLogHandler, NoStacktraceFormatter
from shared.database import DatabaseConfig # pylint: disable=E0401
from shared.google_credentials import GoogleCredentials # pylint: disable=E0401

basedir = os.path.abspath(os.path.dirname(__file__))
ssm_client = boto3.client('ssm', region_name='us-east-2')

def get_env_or_default(env_var, default_value):
    '''
    Returns either the env var value or default specified
    '''
    if env_var in os.environ.keys():
        return os.environ.get(env_var)
    return default_value

def get_config(app):
    '''
    Returns corresponding config instance for environment
    '''
    DEVELOPMENT = int(get_env_or_default("PURSU_DEV", 0)) == 1
    TESTING = int(get_env_or_default("PURSU_TESTING", 0)) == 1
    if DEVELOPMENT:
        config = DevelopmentConfig()
    elif TESTING:
        config = TestingConfig()
    else:
        config = ProductionConfig()
        slack_handler = SlackerLogHandler(
            config.SLACK_TOKEN,
            config.SLACK_CHANNEL,
            stack_trace=True,
            username=config.SLACK_USERNAME
        )
        formatter = NoStacktraceFormatter('%(asctime)s - %(name)s ```%(message)s```')
        slack_handler.setFormatter(formatter)
        slack_handler.setLevel(logging.ERROR)
        app.logger.addHandler(slack_handler)
    return config

def encrypt_token(token, config):
    '''
    Function to encrypt refresh token
    '''
    if token is None:
        return None
    token = token.encode('utf-8')
    encrypted_token = config.TOKEN_CIPHER_SUITE.encrypt(token)
    return encrypted_token.decode('utf-8')

def decrypt_token(token, config):
    '''
    Function to decrypt refresh token
    '''
    if token is None:
        return None
    token = token.encode('utf-8')
    decrypted_token = config.TOKEN_CIPHER_SUITE.decrypt(token)
    return decrypted_token.decode('utf-8')

def get_refresh_token(email, decrypted, appConfig):
    '''
    Function to get refresh token.
    '''
    sql_query = sql.SQL("SELECT token FROM gmail WHERE email={}").format(
        sql.Literal(email))
    token = appConfig.DB_CONN.execute_select_query(sql_query)[0][0]

    if decrypted:
        token = decrypt_token(token, appConfig)

    return token


def validate_keys(dictionary, keys):
    '''
    Function to validate if all the values in the dict are True.
    '''
    return all([True for key in keys if dictionary[key]])


def send_email(config, recipient, subject, message):
    '''
    Function to send email from pursu account
    '''
    sender = config.SENDER
    sender_title = 'Pursu'

    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = formataddr((str(Header(sender_title, 'utf-8')), sender))
    msg['To'] = recipient

    server = smtplib.SMTP_SSL('smtp.zoho.com', 465)

    server.login(sender, config.ZOHO_PASSWORD)
    server.sendmail(sender, [recipient], msg.as_string())
    server.quit()


def init_google_credentials():
    '''
    Responsible for obtaining production credentials from ParameterStore
    '''
    google_creds = []
    params = ssm_client.get_parameters_by_path(Path="/GOOGLE", Recursive=True, WithDecryption=True)\
        ['Parameters']

    index = 0

    # params returned in array with format:
    # [<client_id_1>, <secret_1>, <client_id_2>, <secret_2>, ...]
    while index < len(params):
        # Each pair of indices is a client_id, client_secret pair
        client_id = params[index]['Value']
        client_secret = params[index + 1]['Value']
        google_creds.append({
            'CLIENT_ID': client_id,
            'CLIENT_SECRET': client_secret
        })
        index += 2
    return google_creds

def get_google_project_credentials_for_client_id(appConfig, client_id):
    '''
    Grab relevant google credentials associated with a particular client id
    Returns None if no associated credentials found for client id
    '''
    for gcid, credentials in enumerate(appConfig.GOOGLE_CREDENTIALS):
        if credentials['CLIENT_ID'] == client_id:
            query = sql.SQL("SELECT * FROM google_projects WHERE gcid={}").format(
                sql.Literal(gcid))
            gcid, project_id, topic, has_space = appConfig.DB_CONN.execute_select_query(query)[0]
            return GoogleCredentials(gcid,
                                     project_id,
                                     appConfig.GOOGLE_CREDENTIALS[gcid]['CLIENT_ID'],
                                     appConfig.GOOGLE_CREDENTIALS[gcid]['CLIENT_SECRET'],
                                     topic,
                                     has_space)
    return None

def get_google_project_credentials_for_email(appConfig, email):
    '''
    Grabs relevant google credentials for specific account
    Randomly selects project creds with space if email is not associated with an account
    '''
    query = sql.SQL("SELECT google_projects.* FROM google_projects \
            JOIN gmail ON gmail.gcid=google_projects.gcid WHERE email={}").format(
                sql.Literal(email))
    res = appConfig.DB_CONN.execute_select_query(query)

    if len(res) == 0:
        # If no associated account, select a random project which has space
        query = sql.SQL("SELECT * FROM google_projects WHERE HAS_SPACE=1 \
            ORDER BY RANDOM() LIMIT 1")
        res = appConfig.DB_CONN.execute_select_query(query)

    gcid, project_id, topic, has_space = res[0]
    return GoogleCredentials(gcid,
                             project_id,
                             appConfig.GOOGLE_CREDENTIALS[gcid]['CLIENT_ID'],
                             appConfig.GOOGLE_CREDENTIALS[gcid]['CLIENT_SECRET'],
                             topic,
                             has_space)


class Config:
    '''General Config Variables'''
    def __init__(self):
        # Database config
        self.DATABASE_HOST = ''
        self.DATABASE_NAME = ''
        self.DATABASE_USERNAME = ''
        self.DATABASE_PASSWORD = ''
        self.DATABASE_PORT = ''

        self.DB_CONN = None

        self.TOKEN_CIPHER_SUITE = ''

        self.RATE_LIMITING_ENABLED = True

        # used for sending error messages to our internal ops channel
        self.SLACK_TOKEN = ''
        self.SLACK_CHANNEL = ''
        self.SLACK_USERNAME = ''

        self.AWS_ACCESS_KEY_ID = ''
        self.AWS_SECRET_ACCESS_KEY = ''

        # Houses Google Project credentials
        # Initalize with dummy value because SERIAL gcid starts at 1
        self.GOOGLE_CREDENTIALS = [{'CLIENT_ID': None, 'CLIENT_SECRET': None}]

        # used for recommendation model deployed to AWS Personalize
        self.CAMPAIGN_ARN = '' 

        # used for zoho email client
        self.ZOHO_PASSWORD = ''
        self.SENDER = ''
