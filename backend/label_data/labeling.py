'''
Labelling executable.
'''
import datetime
from io import StringIO, BytesIO
import boto3
import pandas as pd
import click
from shared import config

NUM_ENTRIES = 30

DENYLISTED_TERMS = ['unsubscribe', 'would not like to recieve this type',
                     "don't want to receive this type", 'thanks for filling out',
                     'added a comment', 'replied to a comment',
                     'invitation to edit', 'invited you to view']
DENYLISTED_SUBJECTS = ['automatic reply']

CLIENT = boto3.client('s3',
                      aws_access_key_id=config.Config.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=config.Config.AWS_SECRET_ACCESS_KEY)

# loop over files
def iterate_over_bucket(bucket_name='pursu-trainingdata'):
    '''Method that iterates over a bucket.'''
    paginator = CLIENT.get_paginator('list_objects')
    page_iterator = paginator.paginate(Bucket=bucket_name)
    for page in page_iterator:
        # print(page['Contents'])
        # if page['KeyCount'] > 0:
        if 'Contents' in page:
            for item in page['Contents']:
                yield item['Key']

def find_file():
    ''''Method that finds a file in the bucket'''
    for filename in iterate_over_bucket():
        return filename
    return None

def delete_from_s3(key, bucket_name='pursu-trainingdata'):
    '''Method that deletes from S3'''
    CLIENT.delete_object(Bucket=bucket_name, Key=key)

# check for prefix validity
def is_not_labeled(filename):
    '''Check to see if the filename is labeled.'''
    return str(filename).find('labeled') < 0

# check for relabelled prefix validity
def is_not_relabeled(filename):
    '''Check if the file name is not relabeled.'''
    return str(filename).find('relabeled') < 0

# Print rows & take user input
def label_data(df, relabel_mode=False):
    '''Method that provides the user input to label data.'''
    if relabel_mode:
        labels = list(df['label'])
        relevant = list(df['relevant'])
        df = df.drop('label', axis=1)
        df = df.drop('relevant', axis=1) if 'relevant' in df.columns else df
    else:
        labels = []
        relevant = []

    index = 0
    for subj, body in zip(df['subject'], df['body']):
        if relabel_mode and labels[index] != 7:
            index += 1
            continue

        print("==================================")
        print("Subject: {}".format(subj))
        print("-----------------------")
        print("Content: {}".format(body))
        print("==================================")
        print("Please select one of the following labels:")
        print("[0]: Application Confirmation")
        print("[1]: Referral")
        print("[2]: Coding Challenge")
        print("[3]: Phone Screen")
        print("[4]: Interview")
        print("[5]: Offer")
        print("[6]: Rejection")
        print("[7]: Other/Irrelevant")
        print("[8]: Pre-application contact")
        print("[9]: Post-offer")
        print("==================================")

        label = input("Enter a label: ")
        while (not label.isnumeric()) or int(label) < 0 or int(label) > 9:
            label = input("Enter a valid label: ")

        label = int(label)
        if relabel_mode:
            labels[index] = label
            relevant[index] = 0 if label != 7 else 1
            index += 1
        else:
            labels.append(label)
            relevance = 0 if label != 7 else 1
            relevant.append(relevance)

    df['label'] = labels
    df['relevant'] = relevant
    return df

# Rename file with labeled prefix, and write to labeled S3 bucket
def write_labeled_to_s3(labeled_df):
    '''Method that writes labeled data to S3 bucket.'''
    try:
        file_name = datetime.datetime.now().strftime('%m%d%Y%H%M%S') + '.csv'
        csv_buffer = StringIO()
        labeled_df.to_csv(csv_buffer, index=False)
        CLIENT.put_object(Body=csv_buffer.getvalue(),
                          Bucket='sagemaker-pursu', Key=file_name)
    except Exception as err:
        print(err)

def write_cleaned_data_to_s3(df, file_name):
    '''Method that writes clean data to S3 bucket.'''
    try:
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        CLIENT.put_object(Body=csv_buffer.getvalue(),
                          Bucket='pursu-trainingdata', Key=file_name)
    except Exception as err:
        print(err)

def clean_data():
    """
    Clean the data currently in S3 by removing irrelvant emails.
    Requires all files to be labelled
    """
    removed = 0
    for filename in iterate_over_bucket():
        index = 0
        if is_not_labeled(filename):
            return None

        key = filename
        s3_response_object = CLIENT.get_object(
            Bucket='pursu-trainingdata', Key=key)
        object_content = s3_response_object['Body'].read()
        delete_from_s3(key)
        df = pd.read_csv(BytesIO(object_content), sep=',')

        # Filtering out undesirable entries
        new_data_indexes = []
        for subj, body, label in zip(df['subject'], df['body'], df['label']):
            if label != 7:
                new_data_indexes.append(index)
            elif label == 7 and denylist_filter(subj, body):
                new_data_indexes.append(index)
            else:
                removed += 1
            index += 1

        # Dropping additional columns that have been added
        drop_cols = []
        for col in df.columns:
            if col not in ('subject', 'body', 'label'):
                drop_cols.append(col)

        for col in drop_cols:
            df = df.drop(col, 1)

        new_df = df.iloc[new_data_indexes]
        write_cleaned_data_to_s3(df=new_df, file_name=key)
    return removed

def denylist_filter(subject, body):
    '''Method for a denylist filter.'''
    # if body.find("please") >= 0:
    #     return True

    for term in DENYLISTED_TERMS:
        if body.find(term.lower()) >= 0:
            return False

    for subj in DENYLISTED_SUBJECTS:
        if subject.find(subj.lower()) >= 0:
            return False

    # Special check for quora emails
    words = body.split()
    if words[0] == 'answer':
        return False

    return True

def relabel_data():
    '''Method to relabel data.'''
    key = None
    for filename in iterate_over_bucket():
        if is_not_relabeled(filename):
            key = filename

    if key is None:
        print("All files have been relabeled!")
        return

    s3_response_object = CLIENT.get_object(
        Bucket='pursu-trainingdata', Key=key)
    object_content = s3_response_object['Body'].read()
    delete_from_s3(key)
    df = pd.read_csv(BytesIO(object_content), sep=',')
    relabeled_df = label_data(df, relabel_mode=True)
    write_labeled_to_s3(relabeled_df)


@click.option('--clean', is_flag=True, default=False)
@click.option('--relabel', is_flag=True, default=False)
@click.command()
def main(clean, relabel):
    '''Main method that gets run when executing the file'''
    if clean:
        try:
            conf = input(
                "Please confirm you would like to clean data \
                    and potentially delete datapoints [Y/N]")
        except Exception as err:
            print("Exiting", err)
            return

        if conf == 'Y':
            num_removed = clean_data()
            print("Completed cleaning data! Removed {} rows".format(num_removed))
    elif relabel:
        relabel_data()
        print("Relabeled File")
    else:
        labeled_df = pd.DataFrame()
        for _i in range(NUM_ENTRIES):
            key = find_file()
            if key is None:
                print("No more files remaining!")
                return

            s3_response_object = CLIENT.get_object(
                Bucket='pursu-trainingdata', Key=key)
            object_content = s3_response_object['Body'].read()
            delete_from_s3(key)
            df = pd.read_csv(BytesIO(object_content), sep=',')
            labeled_df = labeled_df.append(label_data(df))
        write_labeled_to_s3(labeled_df)

if __name__ == "__main__":
    main()
