"""
Testing user interaction with blog (index) and blog posts - as well as more
authentification tests.
"""

import pytest
from flaskr.db import get_db

# Test the index page, passing in the test client and the test login.
def test_index(client, auth):
    # Get the response of the index.
    response = client.get('/')
    # Asset an un-logged in user sees the options to Log In and Register.
    assert b"Log In" in response.data
    assert b"Register" in response.data

    # Log the test user in.
    auth.login()
    # Get a new response from the index.
    response = client.get('/')
    # Check the test user has the option to log out.
    assert b'Log Out' in response.data
    # Assert the test blog displays the test data entered in the test SQL
    # database.
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    # Check the test user has the option to update the test post by seeing
    # if the url produced for the update page exists in the response.
    assert b'href="/1/update"' in response.data

# Test the different options a user should have for their own post. As they
# need to be logged in.
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    # Have a non-logged in user try to pass the post method to the different
    # URLs.
    response = client.post(path)
    # As the user is not logged in they should be sent to the login page.
    assert response.headers['Location'] == 'http://localhost/auth/login'

#
def test_author_required(app, client, auth):
    # Change the post auther to another user so that the test user does
    # not match - therefore shouldn't be able to edit, etc.
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    # Log the test user in.
    auth.login()
    # User should not be able to modify the post.
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # Ensure the current user cannot see the edit link.
    assert b'href="/1/update"' not in client.get('/').data

# Check the user cannot edit a post that does not exist.
@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    # Try to pass the post method to a non-existant blog item, should
    # return a Not Found error.
    assert client.post(path).status_code == 404

# Create a test for the user's ability to create a post (add to db).
def test_create(client, auth, app):
    # Have the test user login.
    auth.login()
    # Test access to the create URL for user.
    assert client.get('/create').status_code == 200
    # Perform post method on the create URL to add a blog item to the db.
    client.post('/create', data={'title': 'created', 'body': ''})

    # In the app context, connect to the db to check the existence of the
    # created post.
    with app.app_context():
        db = get_db()
        # Get a count of the posts in the database, should now be 2.
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2

# Test for user's ability to update a created post.
def test_update(client, auth, app):
    auth.login()
    # Check user's ability to update the post.
    assert client.get('/1/update').status_code == 200
    # Run the post method to update the post.
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    # Check the db to see if the post was successfully updated.
    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        # Check the post title is the string 'updated'.
        assert post['title'] == 'updated'

# Check a post cannot be created or updated with invalid data.
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    # Try to create/edit the title to be a blank string and record response.
    response = client.post(path, data={'title': '', 'body': ''})
    # Check existence of the error string.
    assert b'Title is required.' in response.data

# Check the user is able to delete the post and redirected to the
# index page after.
def test_delete(client, auth, app):
    auth.login()
    # Action the deletion of the test post.
    response = client.post('/1/delete')
    # Check user is redirected.
    assert response.headers['Location'] == 'http://localhost/'

    # Check the post has been removed from the database.
    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        # Check no post was returned.
        assert post is None
