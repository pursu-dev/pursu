"""Step 4 of email analysis pipeline. Provides information about email"""
import re
import wordninja
import dateparser
import pytz
from psycopg2 import sql

# pylint: disable=C0330

from email_analysis import appConfig, scrape_email, regex_patterns
from email_analysis import CATEGORIES_TO_LABELS

IGNORED_DOMAINS = ['greenhouse', 'workday', 'facebook-mail', 'gmail']


def preprocess_content(email_info):
    """Fix parsed email content"""
    email_info['body'] = " ".join(wordninja.split(email_info['body']))
    email_info['subject'] = " ".join(wordninja.split(email_info['body']))
    return email_info


def grab_recruiter(email_info, company, college):
    """Returns rid, parses recruiter name from email and insert into database"""
    Patterns = regex_patterns.NamePatterns
    recruiter_keywords = ['recruiting', 'campus']
    coding_challenge_tools = ['hackerrank', 'codility']
    coding_challenge_tools = ['hackerrank', 'codility']

    if email_info['sender'] == '' or company is None:
        return None

    sender = email_info['sender']

    query = sql.SQL("SELECT sender FROM ignore WHERE recruiter=1")
    BLOCKLIST_SENDERS = appConfig.DB_CONN.execute_select_query(query)[0]
    for ignored_sender in BLOCKLIST_SENDERS:
        if sender.find(ignored_sender.lower()) >= 0:
            return None

    names = re.findall(Patterns.FIRST_LAST, sender)
    if len(names) == 0:
        names = re.findall(Patterns.LAST_COMMA_FIRST, sender)
        if len(names) != 0:
            my_names = re.sub(r', ', ' ', names[0]).split()
            names[0] = my_names[1] + " " + my_names[0]

    if email_info['reply_to'] != '' and 'noreply' not in email_info['reply_to']:
        emails = re.findall(regex_patterns.EmailPatterns.EMAIL, email_info['reply_to'])
    else:
        emails = re.findall(regex_patterns.EmailPatterns.EMAIL, sender)

    recruiter_name = None
    recruiter_email = None

    stopwords = recruiter_keywords + coding_challenge_tools
    name_stopwords = stopwords + [company.lower()]
    email_stopwords = stopwords

    if len(names) != 0 and all([
            False for stopword in name_stopwords if stopword in names[0].lower()
    ]):
        recruiter_name = names[0].strip('"').rstrip()
    if len(emails) != 0 and all([
            False
            for stopword in email_stopwords if stopword in emails[0].lower()
    ]):
        recruiter_email = emails[0].strip("<>").rstrip().lower()

    if recruiter_email is not None and recruiter_name is None:
        query = sql.SQL("SELECT name FROM recruiters WHERE UPPER(email)=UPPER({})").format(
            sql.Literal(recruiter_email))
        name_res = appConfig.DB_CONN.execute_select_query(query)
        recruiter_name = name_res[0][0] if name_res != [] else None
    elif recruiter_email is None and recruiter_name is not None:
        query = sql.SQL("SELECT email FROM recruiters WHERE UPPER(name)=UPPER({})").format(
            sql.Literal(recruiter_name))
        email_res = appConfig.DB_CONN.execute_select_query(query)
        recruiter_email = email_res[0][0] if email_res != [] else None

    rid = insert_new_recruiter(recruiter_name, recruiter_email, company)
    if rid is not None:
        insert_college_recruiter_link(college, rid)
    return rid


def process_name(company):
    """Preprocess company name, removing stopwords"""
    search_term = company.lower()
    company_stopwords = [
        r'software', r'co.', r'company', r'trading', r'technologies'
    ]
    for stopword in company_stopwords:
        search_term = re.sub(stopword, '', search_term).rstrip()
    domain_guess = ''.join(search_term.split())
    return domain_guess, search_term


def set_domain(company, domain):
    '''
    Function to set the guessed domain of a company
    '''
    if domain in IGNORED_DOMAINS:
        return
    query = sql.SQL("UPDATE companies SET domain={} WHERE name={}").format(
        sql.Literal(domain), sql.Literal(company))
    appConfig.DB_CONN.execute_update_query(query)


def match_company(email_info, _domain):
    """Attempt to find match from company list in database"""
    query = sql.SQL("SELECT name FROM companies WHERE user_created=0 AND domain IS NULL;")
    temp = appConfig.DB_CONN.execute_select_query(query)

    for company in temp:
        company = company[0]
        d_guess, search_term = process_name(company)

        if d_guess in email_info['sender'].lower(
        ) or search_term in email_info['subject'].lower().split(
        ) or search_term in email_info['body'].lower().split():
            return company

    # At this point, necessary to guess company name from body
    query = sql.SQL("SELECT name FROM companies WHERE user_created=0;")
    temp = appConfig.DB_CONN.execute_select_query(query)

    for company in temp:
        company = company[0]
        if company.lower() in email_info['body'].lower() or company.lower(
        ) in email_info['subject'].lower():
            return company

    return None


def get_company_name(email_info):
    """Return company name associated with passed email"""
    email_addr = ''
    if email_info['reply_to'] != '':
        email_addr = email_info['reply_to']
    else:
        temp = email_info['sender'].split()
        email_addr = temp[-1]

    idx = email_addr.rfind('@')
    domain = email_addr[idx:].strip('<>@')
    idx = domain.rfind('.')
    domain = domain[:idx]

    query = sql.SQL("SELECT name FROM companies WHERE domain={} AND user_created=0").format(
        sql.Literal(domain))
    temp = appConfig.DB_CONN.execute_select_query(query)
    company_name = match_company(email_info,
                                 domain) if temp == [] else temp[0][0]
    return company_name


def get_challenge_link(links):
    """Parse and return coding challenge links from all email links"""
    for link in links:
        temp = link.lower()
        if link_is_valid(temp):
            return link
    return None

def link_is_valid(link):
    """Check for coding challenge link validity"""
    sites = ['hackerrank', 'codility', 'hirevue', 'codesignal',
                       'correlationone', 'pymetrics', 'tara.vitapowered']
    keywords = ['test', 'interview', 'invite', 'start']
    stopwords = ['sample', 'practice', 'info'] # Weed out practice/sample exam links

    return (any([keyword in link for keyword in keywords]) and
            any([site in link for site in sites]) and not
            any([stopword in link for stopword in stopwords]))


def parse_deadline(email_info):
    '''
    Function to parse a deadline from an email using dates in content.
    '''
    #pylint: disable=R0911
    my_settings = {
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': email_info['timestamp'].replace(tzinfo=None),
        'TIMEZONE': 'UTC'
    }
    Patterns = regex_patterns.DatePatterns()
    re_match = re.search(Patterns.STANDARD_DATE, email_info['body'])
    if re_match is not None:
        return dateparser.parse(re_match.group(0), settings=my_settings)

    re_match = re.search(Patterns.FORMAL_DATE, email_info['body'])
    if re_match is not None:
        return dateparser.parse(re_match.group(0), settings=my_settings)

    re_match = re.search(Patterns.MM_DD_YYYY, email_info['body'])
    if re_match is not None:
        return dateparser.parse(re_match.group(0))

    re_match = re.search(Patterns.NATURAL_DEADLINE, email_info['body'])
    if re_match is not None:
        my_match = re_match.group(0)
        my_match = re.sub(r'from today', '', my_match)
        return dateparser.parse(my_match, settings=my_settings)

    re_match = re.search(Patterns.TIME, email_info['body'])
    if re_match is not None:
        return dateparser.parse(re_match.group(0), settings=my_settings)
    return None


def grab_deadline(email_info):
    '''
    Grabs deadline from email info
    '''
    my_deadline = parse_deadline(email_info)

    if my_deadline is not None:
        my_deadline = pytz.utc.localize(my_deadline)
        if my_deadline < email_info['timestamp']:
            my_deadline += (email_info['timestamp'] - my_deadline)
    return my_deadline


def insert_new_recruiter(rec_name, rec_email, company_name):
    """Returns rid and inserts recruiter into the database if new"""
    if any(it is None for it in [rec_name, rec_email, company_name]):
        return None

    cid_query = sql.SQL("SELECT cid FROM companies WHERE name={}").format(sql.Literal(company_name))
    cid_res = appConfig.DB_CONN.execute_select_query(cid_query)
    cid = cid_res[0][0] if cid_res != [] else None

    if cid is not None:
        query = sql.SQL("INSERT INTO recruiters(name, email, cid) \
                VALUES({}, {}, {}) ON CONFLICT(email)\
                DO UPDATE SET updated_at=CURRENT_TIMESTAMP\
                RETURNING rid;").format(
                    sql.Literal(rec_name),
                    sql.Literal(rec_email),
                    sql.Literal(cid)
                )
        rid = appConfig.DB_CONN.execute_insert_return_query(query)
        return rid
    return None


def insert_college_recruiter_link(college, rid):
    '''
    Attempts to insert new college recruiter link if valid college passed in
    If link exists, do nothing
    '''
    if college is None:
        return
    insert_query = sql.SQL("INSERT INTO college_recruiter_link(college, rid) \
                            VALUES({}, {}) ON CONFLICT DO NOTHING"
                          ).format(sql.Literal(college), sql.Literal(rid))
    appConfig.DB_CONN.execute_insert_query(insert_query)


def get_email_information(resp, category, user_email):
    """Provides relevant information about given API response.\
       Returns None for each field that cannot be parsed."""
    response = {}
    email_info = scrape_email.scrape_email_info(resp=resp, to_lower=False)
    email_info['body'] = " ".join(wordninja.split(email_info['body']))
    response['company'] = get_company_name(email_info)

    if category in [CATEGORIES_TO_LABELS['INTERVIEW'],
                    CATEGORIES_TO_LABELS['CODING_CHALLENGE'],
                    CATEGORIES_TO_LABELS['REFERRAL']]:
        college_query = sql.SQL("SELECT U.college FROM users U, gmail G \
            WHERE U.uid = G.uid AND G.email = {}").format(sql.Literal(user_email))
        db_res = appConfig.DB_CONN.execute_select_query(college_query)
        college = db_res[0][0] if db_res != [] else None
        response['rid'] = grab_recruiter(email_info, response['company'], college)
    else:
        response['rid'] = None
    response['timestamp'] = email_info['timestamp']
    response['deadline'] = grab_deadline(email_info)

    if category == CATEGORIES_TO_LABELS['CODING_CHALLENGE']:
        response['challenge_link'] = get_challenge_link(email_info['links'])

    return response
