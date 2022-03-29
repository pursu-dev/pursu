'''
Data Utilization Methods Module
'''
import datetime
from io import StringIO

import boto3
import pandas as pd
from shared import config

def anonymize_and_write_to_S3(email_df, name, user_email):
    '''
    Anonymize and write given email to S3
    '''
    anon_email = [anonymize_email(email_df, name, user_email)]
    anon_email_dataframe = pd.DataFrame(anon_email, columns=['subject', 'body'])
    write_to_s3(anon_email_dataframe)
    return anon_email

def anonymize_email(scraped_email, name, email):
    """
    Anonymizes provided email
    """
    if 'subject' not in scraped_email or 'body' not in scraped_email:
        return None

    if 'sender' in scraped_email:
        names = scraped_email['sender'].split()

        for s_name in names:
            s_name = s_name.lower()
            scraped_email['body'] = scraped_email['body'].replace(
                s_name, ' sender ')
            scraped_email['subject'] = scraped_email['subject'].replace(
                s_name, ' sender ')

    if 'receiver' in scraped_email:
        names = scraped_email['receiver'].split()

        for r_name in names:
            r_name = r_name.lower()
            scraped_email['body'] = scraped_email['body'].replace(
                r_name, ' receiver ')
            scraped_email['subject'] = scraped_email['subject'].replace(
                r_name, ' receiver ')

    names = name.split()
    for part_name in names:
        part_name = part_name.lower()
        scraped_email['body'] = scraped_email['body'].lower().replace(
            part_name, ' anon ')
        scraped_email['subject'] = scraped_email['subject'].lower().replace(
            part_name, ' anon ')

    scraped_email['body'] = scraped_email['body'].replace(email, ' email ')
    scraped_email['subject'] = scraped_email['subject'].replace(
        email, ' email ')

    # Replace punctuation with whitespace
    scraped_email['body'] = scraped_email['body'].replace(',', " ")
    scraped_email['subject'] = scraped_email['subject'].replace(',', " ")

    anon_email = [scraped_email['subject'], scraped_email['body']]
    return anon_email


def write_to_s3(email_df):
    """
    Writes provided email to training data S3 bucket
    """
    try:
        #object = s3.Object('pursu-trainingdata', 's3_key.txt')
        s_3 = boto3.resource('s3', aws_access_key_id=config.Config.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=config.Config.AWS_SECRET_ACCESS_KEY)
        file_name = datetime.datetime.now().strftime('%m%d%Y%H%M%S') + '.csv'
        object = s_3.Object('pursu-trainingdata', key=file_name)
        csv_buffer = StringIO()
        email_df.to_csv(csv_buffer)
        object.put(Body=csv_buffer.getvalue())
    except Exception as err:
        print(err)
