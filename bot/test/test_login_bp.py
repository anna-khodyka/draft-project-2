"""
Testing login blueprint for flask app 'bot'
"""

#pylint: disable=W0614
#pylint: disable=W0613
#pylint: disable=W0401
#pylint: disable=C0413

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append('../')

from init_bp import *
from login_bp import *


def test_login(app, client):
    """
    Testing the /login/logout handler for mongo
    :param app: fixture
    :param client: fixture
    :return:
    """
    response = client.post('/DB_select', data={'db': 'mongodb'})
    assert response.status_code == 302
    assert response.headers['Location']  == 'http://localhost/login/login'

    response = client.post('/login/login', data={'Login': 'test', 'Password': 'test'})
    assert response.headers['Location'] == 'http://localhost/bot-command'

    response = client.post('/login/login', data={'Login': 'test', 'Password': 'wrong'})
    assert b'Incorrect password' in response.data

    response = client.post('/login/login', data={'Login': 'wrong', 'Password': 'wrong'})
    assert b'Incorrect login' in  response.data


def test_login_postgres(app, client):
    """
    Testing the /login/login handler for postgres
    :param app: fixture
    :param client: fixture
    :return:
    """
    response = client.post('/DB_select', data={'db': 'postgres'})
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/login/login'

    response = client.post('/login/login', data={'Login': 'test', 'Password': 'test'})
    assert response.headers['Location'] == 'http://localhost/bot-command'

    response = client.post('/login/login', data={'Login': 'test', 'Password': 'wrong'})
    assert b'Incorrect password' in response.data

    response = client.post('/login/login', data={'Login': 'wrong', 'Password': 'wrong'})
    assert b'Incorrect login' in response.data


def test_logout(app, client):
    """
    Testing the /login/logout handler for mongo
    :param app: fixture
    :param client: fixture
    :return:
    """
    app.before_request_funcs[None] = [before_request]

    response = client.post('/DB_select', data={'db': 'mongodb'})
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/login/login'

    response = client.post('/login/login', data={'Login': 'test', 'Password': 'test'})
    assert response.headers['Location'] == 'http://localhost/bot-command'

    response = client.post('/bot-command', data={'BOT command': 'help'})
    assert response.headers['Location'] == 'http://localhost/help_'

    response = client.post('/login/logout')
    assert response.status_code == 405

    response = client.get('/login/logout')
    assert response.status_code == 302

    response = client.post('/bot-command', data={'BOT command': 'help'})
    assert response.headers['Location'] == 'http://localhost/login/login'

def test_logout_postgres(app, client):
    """
    Testing the /login/logout handler for postgres
    :param app: fixture
    :param client: fixture
    :return:
    """

    app.before_request_funcs[None] = [before_request]

    response = client.post('/DB_select', data={'db': 'postgres'})
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/login/login'

    response = client.post('/login/login', data={'Login': 'test', 'Password': 'test'})
    assert response.headers['Location'] == 'http://localhost/bot-command'

    response = client.post('/bot-command', data={'BOT command': 'help'})
    assert response.headers['Location'] == 'http://localhost/help_'

    response = client.post('/login/logout')
    assert response.status_code == 405

    response = client.get('/login/logout')
    assert response.status_code == 302

    response = client.post('/bot-command', data={'BOT command': 'help'})
    assert response.headers['Location'] == 'http://localhost/login/login'


def test_register(app, client):
    """
    Testing the /login/register handler
    :param app: fixture
    :param client: fixture
    :return:
    """
    response = client.post('/DB_select', data={'db': 'mongodb'})
    assert response.status_code == 302


    response = client.get('/login/register')
    assert b'Register user' in response.data

    users_db = AppUserMongo(user_db)
    response = client.post('/login/register', data={'User_name': 'pytest',
                                                    'Login': 'pytest',
                                                    'Password': 'pytest'})
    assert users_db.get_user('pytest').user_name == 'pytest'

    response = client.post('/login/register', data={'User_name': 'pytest',
                                                    'Login': 'pytest',
                                                    'Password': 'pytest'})
    assert b'already exist' in response.data

    response = client.post('/login/login', data={'Login': 'pytest',
                                                 'Password': 'pytest'})
    assert response.headers['Location'] == 'http://localhost/bot-command'

    assert users_db.delete_user('pytest') == 0

def test_register_postgres(app, client):
    """
    Testing the user registration  in app
    :param app: fixture
    :param client: fixture
    :return:
    """
    response = client.post('/DB_select', data={'db': 'postgres'})
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/login/login'

    response = client.get('/login/register')
    assert b'Register user' in response.data

    users_db = AppUserPSQL(pgsession)

    response = client.post('/login/register', data={'User_name': 'pytest',
                                                    'Login': 'pytest',
                                                    'Password': 'pytest'})
    assert users_db.get_user('pytest').user_name == 'pytest'

    response = client.post('/login/register', data={'User_name': 'pytest',
                                                    'Login': 'pytest',
                                                    'Password': 'pytest'})
    assert b'already exist' in response.data

    response = client.post('/login/login', data={'Login': 'pytest',
                                                 'Password': 'pytest'})
    assert response.headers['Location'] == 'http://localhost/bot-command'

    assert users_db.delete_user('pytest') == 0
