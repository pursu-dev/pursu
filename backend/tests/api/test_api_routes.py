import pytest
import json
import datetime
from email_analysis import LABELS_TO_CATEGORIES, CATEGORIES_TO_LABELS  # pylint: disable=E0401
import api.routes as main_pipeline  # pylint: disable=E0401
import helper  # pylint: disable=E0401


def test_api_health_check(main_api):
    '''
    Test health check route for main api
    '''
    assert main_api.get('/api/health').status_code == 200


def load_test_file(filename):
    '''
    Utility function to load test data file for main api testing. Must be in tests/api/data
    '''
    f = open('tests/api/data/{}'.format(filename), 'r')
    return json.loads(f.read())
