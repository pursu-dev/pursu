"""Training script for the categorization model"""
#pylint: disable=E0611
import os
import glob
import re
import argparse
import logging

from sklearn.externals import joblib
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics

import pandas as pd
import wordninja
import nltk

from utils import generate_vocab, preprocess_data
from utils import vectorize_categorization_layer, LABELS_TO_CATEGORIES

nltk.download('stopwords')

def log_accuracy_measure(y_pred, y_true):
    '''
    Function to log the accuracy from testing
    '''
    perf = metrics.classification_report(
        y_true, y_pred, output_dict=True)

    LOGGER.debug("Layer 4 Evaluation Accuracy:")
    print("\nLayer 4 Evaluation Accuracy:")
    for i in [0, 1, 2, 3, 5, 6, 8, 9]:
        print("{}: {}\n".format(
            LABELS_TO_CATEGORIES[i], perf[str(i)]['precision']))


def read_data(the_args):
    '''
    Function to read data from provided S3 bucket path
    '''
    dir_path = the_args.train
    df = pd.DataFrame()

    for file_name in glob.glob(dir_path+'/*.csv'):
        x = pd.read_csv(file_name, engine='python')
        df = pd.concat([df, x], axis=0)

    df = df[df['label'] != 7]
    df['label'].loc[df['label'] == 4] = 3
    df['text'] = df['subject'] + df['body']

    dicts = generate_vocab(df)
    return df, dicts


if __name__ == '__main__':
    logging.basicConfig()
    LOGGER = logging.getLogger('sagemaker')

    # Create a parser object to collect the environment variables
    parser = argparse.ArgumentParser()

    # Hyperparameters
    parser.add_argument('--num_trees', type=int, default=65)
    parser.add_argument('--seed', type=int, default=7)

    # Other config params
    parser.add_argument('--output-data-dir', type=str,
                        default=os.environ.get('SM_OUTPUT_DATA_DIR'))
    parser.add_argument('--model-dir', type=str,
                        default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str,
                        default=os.environ.get('SM_CHANNEL_TRAIN'))

    args, _ = parser.parse_known_args()

    # Process data for layer4
    dataframe, my_dicts = read_data(args)
    y = dataframe['label'].to_list()
    emails = preprocess_data(dataframe['text'].to_list())

    emails_train, emails_test, y_train, y_test = train_test_split(
        emails, y, test_size=0.2, stratify=y)
    X_train, my_vect = vectorize_categorization_layer(emails_train, my_dicts)
    X_test = my_vect.transform(emails_test)

    # Train model
    cart = DecisionTreeClassifier()
    SEED = 7
    NUM_TREES = 65
    my_model = BaggingClassifier(
        base_estimator=cart, n_estimators=NUM_TREES, random_state=SEED)
    my_model.fit(X_train, y_train)

    # Evaluate training
    preds = my_model.predict(X_test)
    log_accuracy_measure(preds, y_test)

    # Save model and vectorizer to S3
    joblib.dump(my_model, os.path.join(args.model_dir, "layer4model.gz"))
    joblib.dump(my_vect, os.path.join(args.model_dir, 'vectorizer4.pkl'))


def model_fn(model_dir):
    '''
    Function to load model and vectorizer from cached value
    '''
    model = joblib.load(os.path.join(model_dir, "layer4model.gz"))
    vect = joblib.load(os.path.join(model_dir, 'vectorizer4.pkl'))
    return model, vect


def input_fn(request_body, _request_content_type):
    '''
    Function to preprocess input that provided to running endpoint
    '''
    request_body = " ".join(wordninja.split(request_body))
    request_body = re.sub(' [b-hj-tv-z] ', ' ', request_body)
    return request_body


def predict_fn(input_data, model):
    '''
    Function to predict prepocessed input for endpoint
    '''
    clf, vect = model
    test = vect.transform([input_data])
    return clf.predict(test)


def output_fn(prediction, _content_type):
    '''
    Function to process output of endpoint prediction
    '''
    return ",".join([str(pred) for pred in prediction])
