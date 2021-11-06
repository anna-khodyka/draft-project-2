#pylint: disable=W0614
#pylint: disable=W0621
#pylint: disable=W0621
#pylint: disable=W0401
#pylint: disable=C0413
"""
Define fixtures for testing Flask application Bot
"""


from ..main import init_app  # add .. to execute from test folder
import sys
import pytest
from faker import Faker

sys.path.append('../')
fake = Faker()


@pytest.fixture(scope='function')
# @pytest.fixture
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

# @pytest.fixture


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

# c приложения Виталия


# class AuthActions:
#     def __init__(self, client):
#         self._client = client

#     def login(self, username='test', password='test'):
#         # добавить регистрацию

#         return self._client.post(
#             '/auth/login',
#             data={'username': username, 'password': password}
#         )

#     def logout(self):
#         return self._client.get('/auth/logout')


# @pytest.fixture(scope='function')
# def auth_test(client):
#     return AuthActions(client)
