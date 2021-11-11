"""
Defining and Accessing the Database.
https://flask.palletsprojects.com/en/2.0.x/tutorial/database/
"""

# Dependencies.
import sqlite3

import click

# g is a special object, unique for each request.
# Stores data that may be accessed by multiple functions during the request.
# Connection is stored and resused instead of creating a new conection if
# get_db is called a second time in the same request.
from flask import g
# Special object that points to the Flask app handling the request.
from flask import current_app
from flask.cli import with_appcontext


# Will be called when the application has been created and is handling a request.
def get_db():
    if 'db' not in g:
        # Established a connection to the file pointed at by the DATABASE config key.
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Tells the connection to return rows that behave like dicts -
        # can access the columns by name.
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    # Checks is g.db was set - if it was then it closes the connection.
    db = g.pop('db', None)

    if db is not None:
        db.close()
