from init_bp import before_request
from main import init_app
import sys
import os

import flask
from flask import session as flask_session


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append('../')


def test_request_context(app, client):

    app.before_request_funcs[None] = [before_request]
    with app.test_request_context():
        response = client.post('/login/register', data={'User_name': 'pytest',
                                                        'Login': 'pytest',
                                                        'Password': 'pytest'})
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/login/login'
        assert 'db' in flask_session  # не проходит тест
        assert len(flask_session) == 0


def test_session_context(app, client):
    with app.app_context():
        with open('context.log', 'w') as log:
            assert 'db' not in flask_session
            flask_session['db'] = 'choosed'
            assert 'db' in flask_session
            log.write(str(flask_session))
            log.write('\n')
            response = client.post('/login/register', data={'User_name': 'pytest',
                                                            'Login': 'pytest',
                                                            'Password': 'pytest'})
            log.write(str(app.app_ctx_globals_class.pop()))
            log.write('\n')
            assert 'db' in flask_session
