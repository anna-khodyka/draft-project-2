"""
Testing note blueprint of flask app 'bot'
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


def test_find_notes(app, client):
    """
    Testing /note/find_notes handler for postgres db
    :param app: fixture
    :param client: fixture
    :return:
    """

    response = client.get('/note/find_notes')
    assert b'Please input keywords to find note' in response.data

    response = client.get('/note/find_notes',  data={'Keywords': 'man'})
    assert b'Please input keywords to find note' in response.data

    response = client.post('/note/find_notes', data={'Keywords': 'man'})
    assert b'Found some notes' in response.data

    response = client.post('/note/find_notes', data={'Keywords': '^^^^^^^'})
    assert b"I'm really sorry, but this time I couldn't find any notes by your request" in response.data

    response = client.post('/note/find_notes', data={'wrong_': 'man'})
    assert response.status_code == 400


def test_show_all_notes(app, client):
    """
    Testing /note/show_all_notes handler for postgres db
    :param app: fixture
    :param client: fixture
    :return:
    """
    response = client.get('/note/show_all_notes')
    assert b'All the notes I have found in your notebook' in response.data
    assert response.status_code == 200

    response = client.post('/note/show_all_notes')
    assert response.status_code == 405


def test_add_note(app, client):
    """
    Testing /note/add_note' handler for postgres db
    :param app: fixture
    :param client: fixture
    :return:
    """

    response = client.get('/note/add_note')
    assert response.status_code == 200
    assert b'Please input keywords and body for the note' in response.data

    response = client.post('/note/add_note', data={'Keywords': 'flask-test', 'Text': 'some text'})
    assert response.status_code == 200
    assert b'Note successfully saved' in response.data

    note = NotebookPSQL(pgsession)
    notes = note.get_notes('flask-test')
    assert len(notes) == 1

    response = client.post(f'/note/delete_note/{notes[0].note_id}')
    assert b'succesfully deleted' in response.data

    notes= note.get_notes('flask-test')
    assert len(notes) == 0


def test_add_note_wrong_requests(app, client):
    """
    Testing /note/add_note' handler for postgres db with 'invalid' data
    :param app: fixture
    :param client: fixture
    :return:
    """

    response = client.post('/note/add_note',
                           data={'Keywords_wrong': 'flask-test', 'Text': 'some text'})
    assert response.status_code == 400

    response = client.post('/note/add_note',
                           data={'Keywords': 'flask-test', '_Text_': 'some text'})
    assert response.status_code == 400

    response = client.post('/note/add_note',
                           data={'Keywords': 'truncate table contact;', 'Text': 'some text'})
    assert response.status_code == 200

    note = NotebookPSQL(pgsession)
    notes = note.get_notes('truncate')
    assert len(notes) == 1

    response = client.post(f'/note/delete_note/{notes[0].note_id}')
    assert b'succesfully deleted' in response.data


def test_edit_note(app, client):
    """
    Testing /note/edit_note handler for postgres db
    :param app: fixture
    :param client: fixture
    :return:
    """

    response = client.get('/note/edit_note')
    assert response.status_code == 200
    assert b'Please input keywords to find note' in response.data

    response = client.post('/note/edit_note', data={'Keywords': 'man'})
    assert response.status_code == 200
    assert b'All the notes i have found' in response.data

    response = client.post('/note/edit_note', data={'Keyword': 'man'})
    assert response.status_code == 400

def test_save_note(app, client):
    """
    Testing /note/add_note handler for postgres db
    :param app: fixture
    :param client: fixture
    :return:
    """

    response = client.post('/note/add_note', data={'Keywords': 'flask-test', 'Text': 'some text'})
    assert response.status_code == 200
    assert b'Note successfully saved' in response.data

    note = NotebookPSQL(pgsession)
    notes = note.get_notes('flask-test')
    assert len(notes) == 1
    id_= notes[0].note_id

    response = client.get(f'/note/save_note/{id_}')
    assert response.status_code == 200
    assert b'Please edit keywords and body for the note' in response.data


    response = client.post(f'/note/save_note/{notes[0].note_id}',
                           data={'Keywords': 'flask_blind', 'Text': 'barbeque'})
    assert response.status_code == 200
    assert b'Note successfully updated' in response.data

    response = client.post(f'/note/delete_note/{notes[0].note_id}')
    assert b'succesfully deleted' in response.data


def test_delete_note(app, client):
    """
    Testing /note/delete_note handler for postgres db
    :param app: fixture
    :param client: fixture
    :return:
    """

    response = client.get('/note/delete_note')
    assert response.status_code == 200
    assert b'Please input keyword to search the note to delete' in response.data

    response = client.post('/note/delete_note', data={'Keywords': 'man'})
    assert response.status_code == 200
    assert b'Found notes to delete' in response.data

    response = client.post('/note/delete_note', data={'Keyword': 'man'})
    assert response.status_code == 400

