import logging
import pytest
import data_ingestion # noqa: E0401  pylint: disable=E0401

LOGGER = logging.getLogger("testing")

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