"""Utility module for model training and functionality"""

#pylint: disable=R1721
import re
from io import BytesIO
from collections import defaultdict

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn import metrics

import pandas as pd
import boto3
import nltk
import wordninja
from nltk.corpus import stopwords

from shared import config
nltk.download('stopwords')

LABELS_TO_CATEGORIES = {
    0: "APP_CONF",
    1: "REFERRAL",
    2: "CODING_CHALLENGE",
    3: "INTERVIEW",
    5: "OFFER",
    6: "REJECTION",
    7: "IRRELEVANT",
    8: "PRE_APP",
    9: "POST_OFFER"
}


def frequencies(amount, dicts):
    '''
    Function to find term frequencies in corpus
    '''
    output = set()
    for index in range(0, 10):
        if index != 4:
            sorted_dict = {k: v for k, v in sorted(
                dicts[index].items(), key=lambda item: item[1], reverse=True)}
            counter = 0
            for word, _count in sorted_dict.items():
                counter += 1
                if counter <= amount:
                    output.add(word)
    output_list = list(output)
    return output_list


def aggregate_data(model='layer4'):
    '''
    Function to aggregate and slightly format raw email data
    '''
    df = read_files()
    if model == 'layer4':
        df = df[df['label'] != 7]
    labels_list = df['label'].to_list(
    ) if model == 'layer4' else df['relevant'].to_list()
    df['text'] = df['subject'] + df['body']
    email_list = df['text'].to_list()
    return email_list, labels_list


def vectorize_categorization_layer(emails, dicts, amount_in=20):
    '''
    Function to vectorize preprocessed data for categorization
    '''
    vocab = frequencies(amount=amount_in, dicts=dicts)
    vect = CountVectorizer(vocabulary=vocab)
    X = vect.fit_transform(emails)
    return X.toarray(), vect


def generate_vocab(df):
    '''
    Function to generate full vocabulary for categorization layer
    '''
    dicts = []
    for _ in range(0, 10):
        dicts.append(defaultdict(int))

    for text, label in zip(df['text'], df['label']):
        label = int(label)
        try:
            words = text
            words.strip()
            stop_words = stopwords.words('english')
            words = re.sub('[|*-]', ' ', words)
            words = wordninja.split(words)
            words_pruned = []
            custom_stopwords = ['2019', '2020', '2021',
                                'hi', 'sender', 'receiver', 'anon',
                                'us', 'fy', 'one']
            for word in words:
                if len(word) > 1 and word not in stop_words and word not in custom_stopwords:
                    words_pruned.append(word)

            for word in words_pruned:
                dicts[label][word] += 1
        except Exception as e:
            print(e)
    return dicts


def preprocess_data(emails):
    '''
    Function to preprocess data before term vectorization
    '''
    emails = [re.sub('anon', ' ', email) for email in emails]
    emails = [re.sub('sender', ' ', email) for email in emails]
    emails = [re.sub('receiver', ' ', email) for email in emails]
    emails = [" ".join(wordninja.split(email)) for email in emails]
    emails = [re.sub(' [b-hj-tv-z] ', ' ', email) for email in emails]

    return emails


def vectorize_relevance_layer(emails):
    '''
    Function to vectorize emails for the layer 3 model
    '''
    vect = TfidfVectorizer(strip_accents='ascii', ngram_range=(3, 4))
    X = vect.fit_transform(emails).toarray()
    return X, vect


def accuracy_measure(y_pred, y_true):
    '''
    Function to measure the accuracy for a binary output prediction
    '''
    tn, fp, fn, tp = metrics.confusion_matrix(
        y_true, y_pred, labels=[0, 1]).ravel()
    return tp / (tp + fn), tn / (tn + fp)


################ LOCAL HELPERS ##############################
client = boto3.client('s3', aws_access_key_id=config.Config.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=config.Config.AWS_SECRET_ACCESS_KEY)

def iterate_over_bucket():
    '''
    Function to iterate over all files in the S3 bucket
    '''
    paginator = client.get_paginator('list_objects')
    page_iterator = paginator.paginate(Bucket='sagemaker-pursu')

    for page in page_iterator:
        for item in page['Contents']:
            yield item['Key']


def read_files(source='file'):
    '''
    Function to read all of the data files in the given source
    '''
    df = pd.DataFrame()
    if source == 's3':
        gen = iterate_over_bucket()
        while True:
            try:
                key = next(gen)
                s3_response_object = client.get_object(
                    Bucket='sagemaker-pursu', Key=key)
                object_content = s3_response_object['Body'].read()
                df = df.append(pd.read_csv(BytesIO(object_content), sep=','))
                df = df[df['subject'].notnull()]
                df = df[df['body'].notnull()]
                df = df[df['label'].notnull()]
            except StopIteration:
                df.to_csv('training_data.csv')
                break
            except Exception as e:
                print(e)
    else:
        df = pd.read_csv('training_data.csv', sep=',')
    # for index, row in df.iterrows():
    #     process_entry(row['subject'], row['body'], row['label'])
    return df
