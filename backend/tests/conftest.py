'''
Shared resources for testing
'''
import pytest
import sqlite3
import re
import psycopg2
import logging
import json
import testing.postgresql
import helper

LOGGER = logging.getLogger("testing")


@pytest.fixture(name="main_connection", scope='session')
def db_setup_teardown():
    """
    Create connection to in-memory postgresql database.
    """
    with testing.postgresql.Postgresql() as postgresql:
        db_connection = psycopg2.connect(**postgresql.dsn())

        sql_file = open('schema.sql')
        sql_as_string = sql_file.read()
        cur = db_connection.cursor()
        cur.execute(sql_as_string)
        cur.close()

        sql_file = open('tests/sql_setup_commands.sql')
        sql_as_string = sql_file.read()
        cur = db_connection.cursor()
        cur.execute(sql_as_string)
        cur.close()

        # Transfer control to test
        yield db_connection


@pytest.fixture(name='db_conn')
def run_around_tests(main_connection):
    yield main_connection
    helper.clear_database(main_connection)