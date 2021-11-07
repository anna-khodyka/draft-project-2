"""
Testing login blueprint for flask app 'bot'
"""

#pylint: disable=W0614
#pylint: disable=W0613
#pylint: disable=W0401
#pylint: disable=C0413

from login_bp import *
from init_bp import *
from global_var import *
from db_postgres import pgsession
from flask import redirect, url_for, session, render_template, request, app

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append('../')


def test_login_postgres(app, client):
    """
    Testing the /login/login handler for postgres
    :param app: fixture
    :param client: fixture
    :return:
    """
    app.before_request_funcs[None] = [before_request]

    response = client.get('/login/register')
    response = client.post('/login/register', data={'User_name': 'test',
                                                    'Login': 'test',
                                                    'Password': 'test'})

    response = client.post('/login/login', data={'Login': 'test',
                                                 'Password': 'test'})
    assert response.headers['Location'] == 'http://localhost/bot-command'

    response = client.post('/login/login', data={'Login': 'test',
                                                 'Password': 'wrong'})
    assert b'Incorrect password' in response.data

    response = client.post(
        '/login/login', data={'Login': 'wrong', 'Password': 'wrong'})
    assert b'Incorrect login' in response.data


def test_logout(app, client):
    """
    Testing the /login/logout handler
    :param app: fixture
    :param client: fixture
    :return:
    """
    app.before_request_funcs[None] = [before_request]

    response = client.get('/login/register')
    response = client.post('/login/register', data={'User_name': 'test',
                                                    'Login': 'test',
                                                    'Password': 'test'})
    response = client.post(
        '/login/login', data={'Login': 'test', 'Password': 'test'})
    assert response.headers['Location'] == 'http://localhost/bot-command'

    response = client.post('/bot-command', data={'BOT command': 'help'})
    assert response.headers['Location'] == 'http://localhost/help_'

    response = client.post('/login/logout')
    assert response.status_code == 405

    response = client.get('/login/logout')
    assert response.status_code == 302

    response = client.post('/bot-command', data={'BOT command': 'help'})
    assert response.headers['Location'] == 'http://localhost/login/login'


def test_register_postgres(app, client):
    """
    Testing the user registration  in app
    :param app: fixture
    :param client: fixture
    :return:
    """

    response = client.get('/login/register')
    assert b'Register user' in response.data

    app.before_request_funcs[None] = [before_request]

    response = client.get('/login/register')
    assert b'login' in response.data

    assert global_var.users_db is not None

    assert not global_var.users_db.insert_user(
        'test_db_method', "test_db_method", generate_password_hash('test_db_method'))
    assert global_var.users_db.get_user(
        'test_db_method').user_name == 'test_db_method'
    assert global_var.users_db.delete_user('test_db_method') == 0

    response = client.post('/login/register', data={'User_name': 'pytest',
                                                    'Login': 'pytest',
                                                    'Password': 'pytest'})

    assert global_var.users_db.get_user('pytest').user_name == 'pytest'

    response = client.post('/login/register', data={'User_name': 'pytest',
                                                    'Login': 'pytest',
                                                    'Password': 'pytest'})
    assert b'already exist' in response.data

    response = client.post('/login/login', data={'Login': 'pytest',
                                                 'Password': 'pytest'})
    assert response.headers['Location'] == 'http://localhost/bot-command'

    assert global_var.users_db.delete_user('pytest') == 0
