''' Module for filter development '''
import math
from psycopg2 import sql

# 170 terms per query: ~150 companies
# from:{"<c1>" "<c2>" "<c3>" ... } AND {<k1> <k2> <k3> ...}

DENYLISTED_TERMS = ['unsubscribe', 'would not like to recieve this type',
                     "don't want to receive this type", "this message was sent to"]
DENYLISTED_SUBJECTS = ['automatic reply']
OVERRIDE_SUBJECTS = ['you applied for']
PIPELINE_MANAGERS = ['Greenhouse', 'Workday', 'Hire.Lever']
INTERVIEW_PLATFORMS = ['HackerRank', 'Codility', 'CodeSignal', 'HireVue', 'Pymetrics']


def create_filters(appConfig):
    '''
    Function to create filters
    '''
    keywords = '} AND {"coding" "interview" "thank you for applying" \
        "your application" "technical assessment" "coding challenge" "coding assessment" \
            (intern AROUND 5 application) "software engineering" \
                (software AROUND 5 developer) "recruiting" (resume AROUND 10 application)}'

    companies = []
    query = sql.SQL("SELECT name, domain from companies WHERE user_created=0")
    res = appConfig.DB_CONN.execute_select_query(query)

    for row in res:
        if row != []:
            companies.extend(row)

    companies += (PIPELINE_MANAGERS + INTERVIEW_PLATFORMS)

    num_queries = math.ceil(len(companies) / 500)

    queries = ['from:{' for x in range(num_queries)]
    i = 0
    for company in companies:
        company = str(company)
        if company != "nan":
            # Add the company to queries[i]
            queries[i] += ('"' + company + '" ')
            i += 1
            i %= num_queries

    for i, _ in enumerate(queries):
        queries[i] += keywords

    # Get most recent filter version
    query = sql.SQL("SELECT MAX(version) FROM filters")
    db_res = appConfig.DB_CONN.execute_select_query(query)
    last_ver = -1
    if db_res != [] and db_res[0][0] is not None:
        last_ver = db_res[0][0]
    version = last_ver + 1

    # Write new filters to database
    for i, query in enumerate(queries):
        name = 'filt{}'.format(str(i))
        query = sql.SQL("INSERT INTO filters(name, query, version) VALUES({}, {}, {})").format(
            sql.Literal(name), sql.Literal(query), sql.Literal(version))
        appConfig.DB_CONN.execute_insert_query(query)

    return queries, version


def get_filters(appConfig, version=None):
    '''
    Function to get filters
    '''
    query = ''
    if version is None:
        version = get_latest_filter_version(appConfig)
    query = sql.SQL("SELECT query FROM filters WHERE version={}").format(sql.Literal(version))
    queries = appConfig.DB_CONN.execute_select_query(query)
    queries = [q[0] for q in queries]
    return queries


def get_latest_filter_version(appConfig):
    '''
    Function to get latest filter version
    '''
    sql_query = sql.SQL("SELECT MAX(version) FROM filters")
    db_res = appConfig.DB_CONN.execute_select_query(sql_query)
    version = db_res[0][0] if db_res != [] else 0

    if version is None:
        create_filters(appConfig)
        version = 0
    return version


def denylist_filter(appConfig, email_response):
    '''
    Determines whether provided email match is in fact relevant
    '''
    if 'subject' not in email_response or 'body' not in email_response:
        return False

    query = sql.SQL("SELECT sender FROM ignore WHERE company=1")
    DENYLISTED_SENDERS = appConfig.DB_CONN.execute_select_query(query)[0]

    is_relevant = True
    if is_relevant:
        for sender in DENYLISTED_SENDERS:
            if email_response['sender'].find(sender.lower()) >= 0:
                is_relevant = False

    if is_relevant:
        for subj in DENYLISTED_SUBJECTS:
            if email_response['subject'].find(subj.lower()) >= 0:
                is_relevant = False

    if is_relevant:
        for term in DENYLISTED_TERMS:
            if email_response['body'].find(term.lower()) >= 0:
                if email_response['body'].find('please') < 0:
                    is_relevant = False

    if not is_relevant:
        for subj in OVERRIDE_SUBJECTS:
            if email_response['subject'].find(subj.lower()) >= 0:
                is_relevant = True
    return is_relevant
