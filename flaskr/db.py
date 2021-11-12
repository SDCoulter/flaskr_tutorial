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

# Initialize database function.
def init_db():
    # Returns a database connection. Used to execute commands and
    # read from the file.
    db = get_db()

    # Opens a file relative to flaskr/ package (our schema).
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

# Defines a command link command called 'init-db' that calls the init_db
# function and shows a success message to the user.
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the exisiting data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# Register with the Application.
# Writing a function that takes an application and does the registration.
def init_app(app):
    # Tell Flask to call close_db when cleaning up after first response.
    app.teardown_appcontext(close_db)
    # Adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)
