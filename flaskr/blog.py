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

# Create function to get a post from the database.
# Include check_author=True to allow us to display a single post
# on a page and remove the need to check for a user if not required.
def get_post(id, check_author=True):
    # Connect to the database and perform a search for the id.
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # Check the post exists, if not pass the abort exception - 404 not found.
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    # Check the correct user is logged in when editing the post.
    # If not - abort exception, 403 forbidden access.
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    # Otherwise return the post that was found.
    return post

# Define new route to allow user to edit their posts.
# Argument in route allows us to insert the id of the post.
# This is the value that corresponds to the value passed into the function.
# From index.html: url_for('blog.update', id=post['id']) where the id is
# the post value passed in.
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    # Search db for passed in id number, save returned post (or throw error).
    post = get_post(id)

    # If the form is resubmitted.
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        # Validation.
        if not title:
            error = 'Title is required.'
        if not body:
            error = 'Blog post content is required.'

        if error is not None:
            flash(error)
        else:
            # Connect to db and update the row with the new information.
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            # Redirect the user back to the homepage.
            return redirect(url_for('blog.index'))

    # Default page to show. Pass in the post if returned.
    return render_template('blog/update.html', post=post)

# Define blog post deletion route.
@bp.route('/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):
    # Check the post exists in order to delete it.
    get_post(id)
    # Connect to db and run SQL command to delete the post.
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
