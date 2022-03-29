""" Handle data collection for data ingestion """

import time

from apiclient import discovery
import pandas as pd
import httplib2

from data_ingestion import appConfig, scrape_email, data_utils, filters


def gather_training_data(email, creds):
    '''
    Gathers data for a given email
    '''
    _http_auth = creds.authorize(httplib2.Http())
    gmail = discovery.build('gmail', 'v1', credentials=creds)

    # Get query strings
    query_strings = filters.get_filters(appConfig)

    # Get the name of the user to delete later
    name = creds.id_token['name']

    for query in query_strings:
        execute_search(query, gmail, name, email)

    print("Completed data grab for user {}".format(email))


def execute_search(query, gmail, name, email):
    '''
    Execute complete search for one query filter
    '''
    page_token = None
    while True:
        time.sleep(0.1)
        emails = []

        if page_token is None:
            api_res = gmail.users().messages().list(userId='me', q=query).execute()
        else:
            api_res = gmail.users().messages().list(
                userId='me', q=query, pageToken=page_token).execute()

        if 'messages' not in api_res:
            return

        messages = api_res['messages']

        for message in messages:
            msg_id = message['id']
            msg_res = gmail.users().messages().get(userId='me', id=msg_id).execute()
            scraped_email = scrape_email.scrape_email_info(msg_res)

            if scraped_email is not None and filters.denylist_filter(
                    appConfig, scraped_email):
                anon_email = data_utils.anonymize_email(
                    scraped_email, name, email)
                if anon_email is not None:
                    emails.append(anon_email)

        # Convert to data frame and write to the S3 instance
        dataframe = pd.DataFrame(emails, columns=['subject', 'body'])
        data_utils.write_to_s3(dataframe)

        if 'nextPageToken' not in api_res:
            # This was the last result, so we can break
            break
        page_token = api_res['nextPageToken']
