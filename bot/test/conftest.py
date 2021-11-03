#pylint: disable=W0614
#pylint: disable=W0621
#pylint: disable=W0621
#pylint: disable=W0401
#pylint: disable=C0413
"""
Define fixtures for testing Flask application Bot
"""

import sys
import pytest
from faker import Faker

sys.path.append('../')
from main import init_app
fake = Faker()

@pytest.fixture(scope='function')
#@pytest.fixture
def app():
    """
    Launch Flask app with test config
    :return: app Flask app
    """
    app = init_app({
        'TESTING': True,
        'DB_NAME': 'test_contact',
        'SECRET_KEY': b'simple_key',
    })
    yield app

#@pytest.fixture
@pytest.fixture(scope='function')
def client(app):
    """
    Define Flask client
    :param app:
    :return: client
    """
    yield app.test_client()

@pytest.fixture
def runner(app):
    """
    Define cli_runner for Flask app
    :param app:
    :return:
    """
    return app.test_cli_runner()
