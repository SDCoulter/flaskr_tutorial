"""
Test connection to the database - get_db should return the same connection
each time it is called. After the context, the connection should be closed.
"""

# Import the sqlite3 module to work with a db.
import sqlite3

# Import the testing module and the get_db function.
import pytest
from flaskr.db import get_db


# Create function to test getting the db and closing the connection.
def test_get_close_db(app):
    # From the conftest.py file - should initialize the test database.
    with app.app_context():
        # Create a connection to test db and check if the connection is the
        # same.
        db = get_db()
        assert db is get_db()

    # Able to access the attributes of the error by storing it as e.
    # Use pytest.raises as a context manager.
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    # We save the ProgrammingError returned from trying to execute a db
    # statement as e. 'SELECT 1' returns a single column of 1's for every
    # row in the table. We don't need to check the returned data, just
    # the connection to the database - and whether it's closed.
    # The original get_db call is done in a with statement, so the connection
    # should not exist outside it - there should be an error and we check
    # that the error contains the string 'closed'.
    assert 'closed' in str(e.value)


# We also test the CLI command init-db.
# Use the pytest monkeypatch fixture to replace the init_db function
# with one that simply records that it has been called.
def test_init_db_command(runner, monkeypatch):
    # Create a Recorder object that has the single attribute, called.
    # (Inherit from object for compatability?)
    class Recorder(object):
        called = False

    # Create a function to change the attribute to True, to record the
    # function call existence.
    def fake_init_db():
        Recorder.called = True

    # Use monkeypatch to set the attribute to True - ie "call" the flaskr
    # db init_db function, but actually called the fake_init_db function.
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    # We use the runner we created to run the init-db command on the CL.
    result = runner.invoke(args=['init-db'])
    # We store the resulting output as written in db.py.
    # ('Initialized the database.')
    # Assert that the output contains the correct string.
    assert 'Initialized' in result.output
    # Asset that the function init_db has been called.
    assert Recorder.called
