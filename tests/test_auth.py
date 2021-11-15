"""
The register view should render on GET. And it shoudl redirect to the
login URL on POST, and the user's data should be in the database.
We will need to check the error messages shown with invalid data.
"""

import pytest
from flask import g, session
from flaskr.db import get_db

# This function will test get and post methods for the register function.
# Passing in the client and test app.
def test_register(client, app):
    # Test accessing the URL in the client with a get request, if the
    # return status code is 200 then the request was met - no errors.
    assert client.get('/auth/register').status_code == 200
    # Pass the post method to the URL and give a new username and password.
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    # Check that the request was redirected to the login page to login with
    # the newly created credentials.
    # The response comes with a headers attribute that contains the URL address.
    assert 'http://localhost/auth/login' == response.headers['Location']

    # Within the context of the testing app.
    with app.app_context():
        # Run a search in the test db to return the newly created user 'a'.
        # Assert that the respons is not None. (ie does exist.)
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

# Tells pytest to run the same test funxtion with different arguments.
# Using it to test different invalid inputs.
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', 'a', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    # Send the post method to the register page and pass in the arguments
    # featured in parametrize. This tests the three different inputs.
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    # Check the data, as it contains the body of the response as bytes.
    # Must compare bytes to bytes.
    assert message in response.data

# Test for login similar to register - but we want to test the session
# rather than the database (user_id - g, etc).
# We use the auth fixture that we made in the conftest module.
def test_login(client, auth):
    # As before we use the get request to make sure the status code is correct.
    assert client.get('/auth/login').status_code == 200
    # Store response as the AuthActions method login(), where we run the
    # post method on the client /auth/login URL.
    # We use the test login and password as we know this user is in the db.
    response = auth.login()
    # Once logged in we check the test redirects to the index.
    assert response.headers['Location'] == 'http://localhost/'

    # This allows us to access the context variables (session) after the
    # response is returned.
    with client:
        # Get the index page.
        client.get('/')
        # We now have the session variable available to check the logged in
        # user is the correct test user.
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

# Again we add the different invalid entries to test and compare.
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    # We try to login with the invalid test values and compare the responses.
    response = auth.login(username, password)
    assert message in response.data

# Testing the logout should be the opposite of the login testing - we want
# to make sure that session does not contain the user.
def test_logout(client, auth):
    # Login in first with the default testing user and pass.
    auth.login()

    # Use with client to access context variables.
    with client:
        # Log the test user out.
        auth.logout()
        # Assert the user is not in the session.
        assert 'user_id' not in session
