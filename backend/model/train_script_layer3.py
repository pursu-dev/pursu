"""Training script for the relevance model"""

#pylint: disable=E0611
import argparse
import os
import re
import glob
import logging

import wordninja
import pandas as pd

from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB

from utils import preprocess_data, vectorize_relevance_layer, accuracy_measure

def read_data(dir_path):
    '''
    Function to read data from S3 based on provided directory path
    '''
    df = pd.DataFrame()
    for file_name in glob.glob(dir_path+'/*.csv'):
        x = pd.read_csv(file_name, engine='python')
        df = pd.concat([df, x], axis=0)

    return df


if __name__ == '__main__':
    logging.basicConfig()
    LOGGER = logging.getLogger('sagemaker')

    # Create a parser object to collect the environment variables that are in the
    # default AWS Scikit-learn Docker container.
    parser = argparse.ArgumentParser()

    parser.add_argument('--output-data-dir', type=str,
                        default=os.environ.get('SM_OUTPUT_DATA_DIR'))
    parser.add_argument('--model-dir', type=str,
                        default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str,
                        default=os.environ.get('SM_CHANNEL_TRAIN'))
    args = parser.parse_args()

    # Load training data
    dataframe = read_data(args.train)
    dataframe['text'] = dataframe['subject'] + dataframe['body']
    y = dataframe['relevant'].to_list()
    email_list = dataframe['text'].to_list()

    # Preprocess Data
    emails = preprocess_data(email_list)

    # Split into train and testing data
    emails_train, emails_test, y_train, y_test = train_test_split(
        emails, y, test_size=0.2, stratify=y)

    # Vectorize emails for layer3 training
    X_train, vect = vectorize_relevance_layer(emails_train)
    X_test = vect.transform(emails_test)

    model = ComplementNB()
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)
    print("Layer 3 Evaluation Accuracy {}".format(
        accuracy_measure(preds, y_test)))

    # Save the model to the location specified by args.model_dir
    joblib.dump(model, os.path.join(args.model_dir, "layer3Model.gz"))
    joblib.dump(vect, os.path.join(args.model_dir, 'vectorizer3.pkl'))


def model_fn(model_dir):
    '''
    Function to load model and vectorizer from cached value
    '''
    my_model = joblib.load(os.path.join(model_dir, "layer3Model.gz"))
    my_vect = joblib.load(os.path.join(model_dir, 'vectorizer3.pkl'))

    return my_model, my_vect


def input_fn(request_body, _request_content_type):
    '''
    Function to preprocess input that provided to running endpoint
    '''
    request_body = " ".join(wordninja.split(request_body))
    request_body = re.sub(' [b-hj-tv-z] ', ' ', request_body)
    return request_body


def predict_fn(my_input_data, my_model):
    '''
    Function to predict prepocessed input for endpoint
    '''
    clf, my_vect = my_model

    inp = my_vect.transform([my_input_data])
    return clf.predict(inp)


def output_fn(prediction, _content_type):
    '''
    Function to process output of endpoint prediction
    '''
    return ",".join([str(pred) for pred in prediction])
