"""
Initial setup from Flask tutorial.
https://flask.palletsprojects.com/en/2.0.x/tutorial/factory/
"""

# Dependencies.
import os
from flask import Flask

# Factory function.
def create_app(test_config=None):
    # Create Flask instance - files relative to instance folder.
    # Outside flaskr/ folder.
    app = Flask(__name__, instance_relative_config=True)

    # Sets default config that the app will use.
    app.config.from_mapping(
        # Override with random value before deployment.
        SECRET_KEY='dev',
        # Choose the database file/location.
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        # Overrides the default config with values from config.py file - if it exists.
        # Can be used to set a real SECRET_KEY.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in.
        # Configured independently with any development values.
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists.
    # Not done automatically by Flask - needed for SQLite database.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Create a simple route to see application function.
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # Import and call the functions in db.py in this factory.
    from . import db
    # Pass the app to the database to register the other functions.
    db.init_app(app)

    # Import the auth blueprint to register it with the app.
    from . import auth
    # Pass in the blueprint to the app.
    app.register_blueprint(auth.bp)

    return app
