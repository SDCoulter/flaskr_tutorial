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
    assert b"Register" in respons.data

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
