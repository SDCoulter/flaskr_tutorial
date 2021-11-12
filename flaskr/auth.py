"""
*Blueprint* - way to organize a group of related views and other code.
Register views and code with a blueprint rather than directly.
Register the blueprint with the application when available in the factory function.

TUTORIAL: blueprint for authentification, second one for blog posts.
"""

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

# Our function.
from flaskr.db import get_db


# Create a blueprint class.
bp = Blurprint('auth', __name__, url_prefix='/auth')
# Creates Blueprint named auth. The bp needs to know where it's define, so
# __name__ is passed as second argument. And we associate a URL prefix.


# Define a view for users to register.
# Associates the /register URL with the register view function.
# Returns this response when called.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # If user submitted the form, request.method == POST. Validate input.
    if request.method == 'POST':
        # request.form special kind of dict, mapping sumbitted form k and vs.
        username = request.form['username']
        password = request.form['password']
        # Request connection to the database.
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        if not password:
            error = 'Password is required.'

        if error is None:
            try:
                # Create SQL query - (?) replaced by inputs.
                # The database library will take care of escaping the values
                # so you are not vulnerable to a SQL injection attack.
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                # We save the password as a hash for security.

                # Data is modified so .commit() must be called to save the changes.
                db.commit()
            # Defined error if username already exists (from UNIQUE).
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # url_for generates the URL for the login view based on its name.
                # redirect generate a redirect response to the generated URL.
                return redirect(url_for('auth.login'))

        # If validation fails, the error is shown to the user.
        # flash stores messages than can be retrieved when rendering template.
        flash(error)

    # Initial navigation/validation issues require a template to be rendered to user.
    return render_template('auth/register.html')


# Create a view for login.
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # As in register, pull data from submitted form.
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Query database with provided username.
        # Return first (only) result of username in database.
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # If the username does not exist in the database, save error.
        if user is None:
            error = 'Incorrect username.'
        # If the username does exist, check the password hash with the db hash pw.
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # No errors imply correct username and password.
        if error is None:
            # session is a dict that stores data across requests.
            # When validation succeeds, the user's id is stored in a new session.
            # The data is stored in a *cookie* - sent to the browser, and becomes part
            # of subsequent requests. Flask signs this data.
            session.clear()
            session['user_id'] = user['id']
            # Will be available on subsequent requests.
            
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')
