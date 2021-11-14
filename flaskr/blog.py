"""
Blog blueprint.
https://flask.palletsprojects.com/en/2.0.x/tutorial/blog/
"""

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

# Login required function to access blog tools. (Checks user is logged in).
from flaskr.auth import login_required
from flaskr.db import get_db


# Create the Blueprint.
bp = Blueprint('blog', __name__)#, url_prefix='/blog')
# Tutorial does not require url_prefix.


# Define the route for the blog.
# Index will show all the posts that were made thus far.
@bp.route('/')
def index():
    # Request connection to the database.
    db = get_db()

    # Get the posts from the database.
    # Join with users table to get corresponding user id numbers.
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    # Render the template with the posts, pass the posts into the page.
    return render_template('blog/index.html', posts=posts)

# Define a route for a user to create a blog post.
# Use the decorator to ensure the user is logged in before being able to access
# the create blog post page.
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    # Check that a form has been submitted.
    if request.method == 'POST':
        # Store submitted data.
        title = request.form['title']
        body = request.form['body']
        error = None

        # Validation.
        if not title:
            error = 'Title is required.'
        if not body:
            error = 'Blog post content is required.'

        # Check no errors, flash otherwise, as in previous.
        if error is not None:
            flash(error)
        else:
            # Request db connection.
            db = get_db()
            # Add the new post to the database.
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            # Commit the changes to the database (data modification).
            db.commit()
            # Return user to homepage to see their new post.
            return redirect(url_for('blog.index'))

    # If there is no POST method, render the template empty.    
    return render_template('blog/create.html')
