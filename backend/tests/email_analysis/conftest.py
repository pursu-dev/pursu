import logging
import pytest
from cryptography.fernet import Fernet

import email_analysis # noqa: E0401  pylint: disable=E0401

LOGGER = logging.getLogger("testing")

@pytest.fixture(name="email_api")
def email_client_setup_teardown(db_conn):
    """
    Start a Flask test server for email analysis pipeline
    """
    LOGGER.info("Setup test fixture 'email_api'")

    # Configure Flask test server
    email_analysis.appConfig.DB_CONN.conn = db_conn
    email_analysis.appConfig.TOKEN_CIPHER_SUITE = Fernet(Fernet.generate_key())

    # Transfer control to test
    with email_analysis.app.test_client() as client:
        yield client

    LOGGER.info("Teardown test fixture 'email_api'")