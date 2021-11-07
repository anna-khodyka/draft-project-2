"""
Testing the init blueprint of flask app 'bot'
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
if True:
    from login_bp import *
    from main import *
    from init_bp import *


def test_init_app():
    """
    Testing if flask run with test config
    :return:
    """
    assert not init_app().testing  # assert default config is not testing
    assert not init_app().debug  # assert default config is not debug


def test_app_routes(app, client):
    """
    Testing all the routes of flask app
    :param app: fixture
    :param client: fixture
    :return:
    """
    app.before_request_funcs[None] = [before_request]

    routes = [
        '/',
        '/bot-command',
        '/help_',
        '/hello_',
        '/login/login',
        '/login/logout',
        '/login/register',
        '/note/find_notes',
        '/note/show_all_notes',
        '/note/add_note',
        '/note/edit_note',
        '/note/save_note/1000001',
        '/note/delete_note',
        '/note/delete_note//1000001',

    ]
    for route in routes:
        assert client.get(route).status_code in [200, 204, 302, 308]


def test_before_request(app, client):
    """
    Testing the before_request middlewre
    :param app: fixture
    :param client: fixture
    :return:
    """
    app.before_request_funcs[None] = [before_request]

    response = client.get('/help_')
    assert response.headers['Location'] == 'http://localhost/login/login'
    response = client.post('/login/register', data={'User_name': 'test',
                                                    'Login': 'test',
                                                    'Password': 'test'})
    response = client.post(
        '/login/login', data={'Login': 'test', 'Password': 'test'})
    assert response.headers['Location'] == 'http://localhost/bot-command'


def test_bot(app, client,  auth_test):
    """
    Testing the /bot-command handler
    :param app: fixture
    :param client: fixture
    :return:
    """
    auth_test.login()
    response = client.get('/bot-command')
    assert response.status_code == 200

    response = client.post('/bot-command', data={'BOT command': ''})
    assert response.headers['Location'] == 'http://localhost/help_'

    auth_test.logout()
    response = client.post('/bot-command', data={'BOT command': ''})
    assert response.headers['Location'] == 'http://localhost/login/login'
