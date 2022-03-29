'''
Module for insight 2 update jobs
'''

from datetime import datetime
from io import StringIO
import pandas as pd
import boto3

def update_pipelines(appConfig):
    '''
    Function to update pipelines file in S3 bucket for insight #2
    '''
    client = boto3.client('s3', aws_access_key_id=appConfig.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=appConfig.AWS_SECRET_ACCESS_KEY)
    df = get_pipelines(appConfig)
    df = df.append(get_old_pipelines(client))
    write_pipelines_to_s3(df, client)


def get_pipelines(appConfig):
    '''
    Function to retrieve current pipelines from database
    '''
    query = "SELECT uid, cid, timestamp FROM pipelines;"
    db_res = appConfig.DB_CONN.execute_select_query(query)
    pipelines = [list(res) for res in db_res]
    return extract_timestamps(pipelines)


def extract_timestamps(pipelines):
    '''
    Function to convert pipeline timestamps to usable form for AWS
    '''
    for row in pipelines:
        try:
            date_str = datetime.strptime(str(row[2]), "%Y-%m-%d %H:%M:%S.%f%z")
        except ValueError:
            date_str = datetime.strptime(str(row[2]), "%Y-%m-%d %H:%M:%S%z")
        row[2] = int(date_str.replace(microsecond=0).timestamp())
    df = pd.DataFrame(data=pipelines, columns=["USER_ID", "ITEM_ID", "TIMESTAMP"])
    return df


def get_old_pipelines(client):
    '''
    Function to retrieve old pipelines file from S3
    '''
    old_pipelines_csv = client.get_object(Bucket="personalize-insight2", Key="old_pipelines.csv")
    return pd.read_csv(old_pipelines_csv['Body'])


def write_pipelines_to_s3(df, client):
    '''
    Function to write update pipelines file to S3
    '''
    csv_buffer = StringIO()
    df.to_csv(path_or_buf=csv_buffer, index=False)
    client.put_object(
        Body=csv_buffer.getvalue(),
        Bucket="personalize-insight2",
        Key="pipelines.csv")
