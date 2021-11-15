"""
Testing the factory function (create_app) by passing in a fixture.
"""

# Import the function to test.
from flaskr import create_app


# Create a function to test the config argument in create_app.
def test_config():
    # Create assert statement to test condition and trigger an error if the
    # condition is false. So trigger an error if already testing.
    assert not create_app().testing
    # Pass in the argument to test the create_app function.
    assert create_app({'TESTING': True}).testing


# Test the hello route we created as a test in the factory function.
def test_hello(client):
    # Get the response from getting to the route test of '/hello'.
    response = client.get('/hello')
    # Check the binary expected response with the test response.
    # Use assert to trigger an error if the results do not match.
    assert response.data == b'Hello, World!'
