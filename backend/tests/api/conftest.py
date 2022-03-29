import logging
import pytest
from cryptography.fernet import Fernet

import api # noqa: E0401  pylint: disable=E0401

LOGGER = logging.getLogger("testing")

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