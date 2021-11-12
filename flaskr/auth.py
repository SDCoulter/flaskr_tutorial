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

# Once the user's id is stored in the session, it will be available on subsequent requests.
# At the beginning of each request, if logged in, user information should be loaded and
# made available to other views.

# Registers a function to run before view function, no matter requested URL.
@bp.before_app_request
def load_logged_in_user():
    # Checks if user id is stored in the session and gets data from db if so.
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        # Store the data in g.user if so, which lasts the length of the request.
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# Create logout view to remove user from the session.
@bp.route('/logout')
def logout():
    # Clear the session if this route is viewed.
    session.clear()
    # Return home.
    return redirect(url_for('index'))

# Create decorator for further authentification - check this for each view it's applied to.
# Returns a new view function that wraps the original view it is applied to.
def login_required(view):
    @functools.wraps(view):
    def wrapped_view(**kwargs):
        # Checks if a user is loaded and redirects to the home page otherwise.
        if g.user is NOne:
            return redirect(url_for('auth.login'))

        # Wraps the original view.
        # If a user is loaded the original view is called and continues normally.
        return view(**kwargs)

    # Runs and returns the function above.
    return wrapped_view
