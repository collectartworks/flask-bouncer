"""Contains all fabric tasks.

This module includes a bunch of management tasks that are used to set up
the environment and run tests.

Please only use this module in conjunction with fabric.
This module is not meant to be imported.
"""

from fabric.api import local, task


@task
def requirements():
    """Setup local development virtualenv."""
    local("virtualenv -p python3 venv")
    local("venv/bin/pip install --upgrade pip")
    local("venv/bin/pip install -r requirements.txt")


@task
def run_tests():
    """Run lokal tests."""
