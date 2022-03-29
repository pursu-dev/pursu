import logging
import pytest

from shared import config # pylint: disable=E0401

@pytest.fixture(name="appConfig")
def generate_app_config(db_conn):
    appConfig = config.TestingConfig()
    appConfig.DB_CONN.conn = db_conn
    yield appConfig