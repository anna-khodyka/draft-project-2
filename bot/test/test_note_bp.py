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
if True:
    from init_bp import *


def create_test_note_and_tag(app, client):
    users_db = AppUserPSQL(pgsession)
    test_user_id = users_db.get_user('test').user_id
    notes_db = NotebookPSQL(pgsession)
    notes_db.create_tag(test_user_id, 0, "test_tag")
    tags = notes_db.get_all_tags(test_user_id)
    assert len(tags) == 2
    assert notes_db.insert_note(test_user_id, tags, 'test note text')

    notes = notes_db.get_notes(test_user_id, "test")
    assert len(notes)  # == 1
    test_note_id = notes[0].note_id
    assert len(notes_db.get_all_notes(test_user_id))  # == 1

    return test_user_id, test_note_id


def delete_all_test_notes_and_tags(app, client):
    users_db = AppUserPSQL(pgsession)
    test_user_id = users_db.get_user('test').user_id
    notes_db = NotebookPSQL(pgsession)
    notes_list = notes_db.get_all_notes(test_user_id)
    for note in notes_list:
        notes_db.delete_note(note.note_id)
    assert len(notes_db.get_all_notes(test_user_id)) == 0


def test_find_notes(app, client, auth_test):
    """
    Testing /note/find_notes handler for postgres db
    :param app: fixture
    :param client: fixture
    :return:
    """
    auth_test.login()

    response = client.get('/note/find_notes')
    assert b'Please input keywords to find note' in response.data

    create_test_note_and_tag(app, client)

    response = client.get('/note/find_notes',  data={'Keywords': 'test_tag'})
    assert b'Please input keywords to find note' in response.data

    response = client.post('/note/find_notes', data={'Keywords': '^^^^^^^'})
    assert b"I'm really sorry, but this time I couldn't find any notes by your request" in response.data

    response = client.post('/note/find_notes', data={'wrong_': 'test_tag'})
    assert response.status_code == 400

    response = client.post(
        '/note/find_notes', data={'Keywords': 'test'})
    response.status_code == 200
    assert b'Found some notes' in response.data
    assert b'All the notes i have found' in response.data

    delete_all_test_notes_and_tags(app, client)


def test_show_all_notes(app, client, auth_test):
    """
    Testing /note/show_all_notes handler for postgres db
    :param app: fixture
    :param client: fixture
    :return:
    """
    auth_test.login()

    create_test_note_and_tag(app, client)

    response = client.get('/note/show_all_notes')
    assert b'All the notes I have found in your notebook' in response.data
    assert response.status_code == 200

    response = client.post('/note/show_all_notes')
    assert response.status_code == 405

    delete_all_test_notes_and_tags(app, client)


def test_add_note(app, client, auth_test):
    """
    Testing /note/add_note' handler for postgres db
    :param app: fixture
    :param client: fixture
    :return:
    """
    auth_test.login()
    users_db = AppUserPSQL(pgsession)
    test_user_id = users_db.get_user('test').user_id
    notes_db = NotebookPSQL(pgsession)

    response = client.get('/note/add_note')
    assert response.status_code == 200
    assert b'Please select tags and create the body for a new note' in response.data

    notes_db.create_tag(test_user_id, 0, "private")

    # creating list of tags id to use it in post-request
    tags = notes_db.get_all_tags(test_user_id)
    tag_id_list = []
    for tag in tags:
        tag_id_list.append(tag[1])

    response = client.post(
        '/note/add_note', data={'Tags': tag_id_list, 'Text': 'my private note'})
    assert response.status_code == 200
    assert b'Note successfully saved' in response.data

    notes = notes_db.get_notes(test_user_id, 'private')
    assert len(notes) == 1

    # checking post-request with wrong data
    response = client.post('/note/add_note',
                           data={'Tags': tag_id_list, '_Text_': 'some text'})
    assert response.status_code == 400

    response = client.post(f'/note/delete_note/{notes[0].note_id}')
    assert b'succesfully deleted' in response.data

    notes = notes_db.get_notes(test_user_id, 'my private note')
    assert len(notes) == 0


def test_edit_note(app, client, auth_test):
    """
    Testing /note/edit_note handler for postgres db
    :param app: fixture
    :param client: fixture
    :return:
    """
    auth_test.login()

    create_test_note_and_tag(app, client)

    response = client.get('/note/edit_note')
    assert response.status_code == 200
    assert b'Please input keywords to find note' in response.data

    response = client.post('/note/edit_note', data={'Keywords': 'test'})
    assert response.status_code == 200
    assert b'All the notes i have found' in response.data

    response = client.post('/note/edit_note', data={'Keyword': 'test'})
    assert response.status_code == 400

    delete_all_test_notes_and_tags(app, client)


def test_save_note(app, client, auth_test):
    """
    Testing /note/add_note handler for postgres db
    :param app: fixture
    :param client: fixture
    :return:
    """
    auth_test.login()
    test_user_id, test_note_id = create_test_note_and_tag(app, client)

    response = client.get(f'/note/save_note/{test_note_id}')
    assert response.status_code == 200
    assert b'Please edit keywords and body for the note' in response.data

    # creating list of tags id to use it in post-request
    notes_db = NotebookPSQL(pgsession)
    tags = notes_db.get_all_tags(test_user_id)
    tag_id_list = []
    for tag in tags:
        tag_id_list.append(tag[1])

    response = client.post(f'/note/save_note/{test_note_id}',
                           data={"Tags": tag_id_list, 'Text': 'barbeque'})
    assert response.status_code == 200
    assert b'Note successfully updated' in response.data

    delete_all_test_notes_and_tags(app, client)


def test_delete_note(app, client, auth_test):
    """
    Testing /note/delete_note handler for postgres db
    :param app: fixture
    :param client: fixture
    :return:
    """
    auth_test.login()

    test_user_id, test_note_id = create_test_note_and_tag(app, client)

    response = client.get('/note/delete_note')
    assert response.status_code == 200
    assert b'Please input keyword to search the note to delete' in response.data

    response = client.post('/note/delete_note', data={'Keywords': 'test'})
    assert response.status_code == 200
    assert b'Found notes to delete' in response.data

    response = client.post('/note/delete_note', data={'Keyword': 'test'})
    assert response.status_code == 400

    response = client.post(f'/note/delete_note/{test_note_id}')
    assert response.status_code == 200
    assert b'succesfully deleted' in response.data
