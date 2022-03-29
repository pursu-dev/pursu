'''
Main api util functions
'''

# pylint: disable=E1101
from psycopg2 import sql
from apiclient import discovery
import httplib2

from api import filters, get_credentials, appConfig


def user_exists(email):
    '''
    Function to determine if user exists.
    '''
    sql_query = sql.SQL("SELECT * FROM gmail WHERE email={}").format(sql.Literal(email))
    row_count = appConfig.DB_CONN.execute_select_query(sql_query)
    return row_count != []


def user_in_beta(email):
    '''
    Function to determine if user is in private beta.
    '''
    sql_query = sql.SQL("SELECT * FROM beta_users WHERE email={}").format(sql.Literal(email))
    row_count = appConfig.DB_CONN.execute_select_query(sql_query)
    return row_count != []


def update_user_filters(email, label_id):
    '''
    Function to update pursu filters with latest version
    '''
    creds = get_credentials(email, appConfig)
    delete_old_user_filters(creds=creds, email=email, label_id=label_id)
    add_filters(creds=creds, email=email, label_id=label_id)


def add_filters(creds, email, label_id):
    '''
    Function to add filters.
    '''
    _httpauth = creds.authorize(httplib2.Http())
    gmail = discovery.build('gmail', 'v1', credentials=creds)

    filter_queries = filters.get_filters(appConfig)

    for critera in filter_queries:
        reqs = {
            'criteria': {
                'query': critera
            },
            'action': {
                'addLabelIds': [label_id]
            }
        }
        _filter = gmail.users().settings().filters().create(
            userId=email, body=reqs).execute()


def delete_old_user_filters(creds, email, label_id):
    '''
    Function to delete old pursu-generated filters for passed-in user email
    '''
    gmail = discovery.build('gmail', 'v1', credentials=creds)
    filts = gmail.users().settings().filters().list(userId=email).execute()

    if 'filter' not in filts:
        return
    for filt in filts['filter']:
        if 'action' in filt and 'addLabelIds' in filt['action']:
            if label_id in filt['action']['addLabelIds']:
                gmail.users().settings().filters().delete(userId=email, id=filt['id']).execute()

def manually_update_filters():
    '''
    Function to manually update filters for all users
    '''
    query = "SELECT email, label FROM gmail G, users U WHERE G.uid=U.uid AND U.active=1;"
    db_res = appConfig.DB_CONN.execute_select_query(query)

    for [email, label] in db_res:
        try:
            update_user_filters(email, label)
            print("Updated email: {}".format(email))
        except Exception as e:
            print(e)

def transfer_user_account(uid, email):
    '''
    Function to transfer user account to a new uid. Returns new uid
    '''
    select_query = sql.SQL("SELECT name, filt_version, college, major, year, consent, gender, \
                           ethnicity FROM users WHERE uid={}").format(sql.Literal(uid))
    db_res = appConfig.DB_CONN.execute_select_query(select_query)
    [name, filt_version, college, major, year, consent, gender, ethnicity] = db_res[0]

    update_query = sql.SQL("UPDATE users SET name='ANON', gender=3, ethnicity='ANON', active=0\
                           WHERE uid={}").format(sql.Literal(uid))
    appConfig.DB_CONN.execute_update_query(update_query)

    sql_query = sql.SQL("INSERT INTO \
        users(name, filt_version, college, major, year, consent, gender, ethnicity) \
        VALUES({}, {}, {}, {}, {}, {}, {}, {}) RETURNING uid").format(
            sql.Literal(name), sql.Literal(filt_version), sql.Literal(college), sql.Literal(major),
            sql.Literal(year), sql.Literal(consent), sql.Literal(gender), sql.Literal(ethnicity)
            )
    new_uid = appConfig.DB_CONN.execute_insert_return_query(sql_query)

    sql_query = sql.SQL("UPDATE gmail SET uid={} WHERE email={}").format(
                sql.Literal(new_uid), sql.Literal(email))
    appConfig.DB_CONN.execute_update_query(sql_query)
    return new_uid
