'''
Module to store labeled data
'''
import datetime
from io import StringIO, BytesIO
import time
import pdb
import boto3
import pandas as pd
from labeling import iterate_over_bucket, delete_from_s3
from shared import config

CLIENT = boto3.client('s3',
                      aws_access_key_id=config.Config.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=config.Config.AWS_SECRET_ACCESS_KEY)

def move_data_to_sagemaker():
    '''Function to move data to sagemaker'''
    for filename in iterate_over_bucket():
        s3_response_object = CLIENT.get_object(
            Bucket='pursu-trainingdata', Key=filename)
        object_content = s3_response_object['Body'].read()
        df = pd.read_csv(BytesIO(object_content), sep=',')

        delete_from_s3(filename)

        new_name = datetime.datetime.now().strftime('%m%d%Y%H%M%S') + '.csv'
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        CLIENT.put_object(Body=csv_buffer.getvalue(),
                          Bucket='sagemaker-pursu', Key=new_name)
        time.sleep(1)

def modify_labels():
    '''Function to modify labels'''
    count = 0
    pdb.set_trace()
    for filename in iterate_over_bucket('sagemaker-pursu'):
        s3_response_object = CLIENT.get_object(
            Bucket='sagemaker-pursu', Key=filename)
        object_content = s3_response_object['Body'].read()
        df = pd.read_csv(BytesIO(object_content), sep=',')
        delete_from_s3(filename, 'sagemaker-pursu')

        # Dropping additional columns that have been added
        drop_cols = []
        for col in df.columns:
            if col not in ('subject', 'body', 'label'):
                drop_cols.append(col)

        for col in drop_cols:
            df = df.drop(col, 1)

        relv = []
        for label in df['label']:
            if label == 7:
                relv.append(1)
            else:
                relv.append(0)

        df['relevant'] = relv

        new_name = datetime.datetime.now().strftime('%m%d%Y%H%M%S') + '.csv'
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        CLIENT.put_object(Body=csv_buffer.getvalue(),
                          Bucket='sagemaker-pursu', Key=new_name)

        print("Completed file {}".format(count))
        count += 1
        time.sleep(1)

if __name__ == '__main__':
    modify_labels()
