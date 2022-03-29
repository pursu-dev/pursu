import logging
import pytest
import api
import data_ingestion
from cryptography.fernet import Fernet

from shared import config # pylint: disable=E0401

LOGGER = logging.getLogger("testing")

@pytest.fixture(name="appConfig")
def generate_app_config(db_conn):
    appConfig = config.TestingConfig()
    appConfig.DB_CONN.conn = db_conn
    yield appConfig

@pytest.fixture(name="data_api")
def data_client_setup_teardown(db_conn):
    """
    Start a Flask test server for data ingestion pipeline
    """
    LOGGER.info("Setup test fixture 'data_api'")

    # Configure Flask test server
    data_ingestion.appConfig.DB_CONN.conn = db_conn

    # Transfer control to test
    with data_ingestion.app.test_client() as client:
        yield client
    LOGGER.info("Teardown test fixture 'data_api'")

@pytest.fixture(name="main_api")
def api_client_setup_teardown(db_conn):
    """
    Start a Flask test server for main application api
    """
    LOGGER.info("Setup test fixture 'main_api'")

    # Configure Flask test server
    api.appConfig.DB_CONN.conn = db_conn
    api.appConfig.TOKEN_CIPHER_SUITE = Fernet(Fernet.generate_key())

    # Transfer control to test
    with api.app.test_client() as client:
        yield client

    LOGGER.info("Teardown test fixture 'main_api'")