"""
Making the Project Installable:
https://flask.palletsprojects.com/en/2.0.x/tutorial/install/
"""

from setuptools import find_packages, setup

# Create a setup that can install the application.
setup(
    name='flaskr',
    version='1.0.0',
    # Tells Python what package directories (and Python files) to include.
    packages=find_packages(),
    # Includes the other folders, like static and templates.
    # Requires input file: MANIFEST.in
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)
