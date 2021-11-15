"""
Contains the setup functions (fixtures) that each test will use.
Test modules start with test_.
Each test creates a new temp db file.

App fixture will call the factory and pass test_config to configure the
application and databse for testing instead of local development.
"""

import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

# Read the SQL file.
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

# Define a fixture (setup function) for a test.
@pytest.fixture
def app():
    # Create and open temp file, returning the descriptor and path.
    db_fd, db_path = tempfile.mkstemp()

    # Overwrite the actual db path with the test one.
    app = create_app({
        # Tells Flask the app is in test mode.
        'TESTING': True,
        'DATABASE': db_path,
    })

    # Connect to the temp db file, not the actual one.
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    # Return the app as a generator.
    yield app

    # Close the connection and link to the temp db file.
    os.close(db_fd)
    os.unlink(db_path)

# Calls app.test_client() withb the application object created by
# the app fixture (above). Tests will use the client to make requests
# to the app without running the server.
@pytest.fixture
def client(app):
    return app.test_client()

# Similar to the client fixture. Creates a runner that can call the
# CLick commands registered with the application.
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

# Pytest uses fixtures by matching their function names with the names
# of arguments in the test funtions.
# We will pass in the name of the fixtures to the test functions.


# Create a class with methods to test authentification. The class will make
# POST requests to the views with the client. We will use a fixture to pass
# it the client for each test.
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)
