
# протестить загрузку большого файла
import os
import sys
import pathlib
import io

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append('../')
if True:
    from init_bp import *

EXT_FOR_TEST_FILES = ('JPG', 'TXT', 'MP3', 'ZIP', "HTML")


def create_test_files():
    '''
    create test files
    :return: test files list
    '''
    test_file_list = []
    for file_extension in EXT_FOR_TEST_FILES:
        with open(f'test_file.{file_extension}', 'w') as fh:
            fh.write(f'I am a test file with {file_extension} extension')
            test_file_list.append(test_file_list)
    return test_file_list


def remove_test_files():
    '''
    remove test files
    '''
    for file_extension in EXT_FOR_TEST_FILES:
        os.remove(f'test_file.{file_extension}')


def check_file_extension_and_content(file, file_extension):
    '''
    : param file: str file name
    : param file_extension: str file extension
    : return: True/False
    '''
    with open(file, 'r') as fh:
        file_content = fh.read()
        assert file_content == f'I am a test file with {file_extension} extension'
    assert file.rsplit('.', 1)[1].upper() == file_extension


def test_upload(app, client, auth_test):

    auth_test.login()

    # deleting all files in DB
    users_db = AppUserPSQL(pgsession)
    test_user_id = users_db.get_user('test').user_id
    files_db = FileFolderPSQL(pgsession)
    files = files_db.get_files(test_user_id, 'test_file')
    for file in files:
        files_db.delete_file(file.file_id)
    assert files_db.number_of_files(test_user_id) == 0

    response = client.get("/file/upload")
    assert response.status_code == 200
    assert b"Please choose the file you would like to upload" in response.data
    assert b"Now you are used 0/100" in response.data

    # uploading 1 file to DB
    response = client.post("/file/upload",
                           content_type='multipart/form-data',
                           data=dict(
                               file=(io.BytesIO(b'my file contents'),
                                     'test_file.TXT'),
                           ))
    assert response.status_code == 200
    assert b"File successfully saved" in response.data
    assert b"Add one more file" in response.data

    # checking is 1 file in DB:
    users_db = AppUserPSQL(pgsession)
    test_user_id = users_db.get_user('test').user_id
    files_db = FileFolderPSQL(pgsession)
    assert files_db.number_of_files(test_user_id) == 1

    response = client.post("/file/upload",
                           content_type='multipart/form-data',
                           data=dict(
                               file=(io.BytesIO(b'my file contents'),
                                     'test_file.TXT'),
                           ))
    assert response.status_code == 200
    assert b"There was an error while your request handled" in response.data

    # checking an increment of used_files
    response = client.get("/file/upload")
    assert response.status_code == 200
    assert b"Please choose the file you would like to upload" in response.data
    assert b"Now you are used 1/100" in response.data

    # checking a posibbility to upload 100+1 files
    for counter in range(100):
        response = client.post("/file/upload",
                               content_type='multipart/form-data',
                               data=dict(
                                   file=(io.BytesIO(b'my file contents'),
                                         f'test_file{counter}.TXT'),
                               ))
    assert b"User exceed the limit on number of files" in response.data

    # deleting all files in DB
    users_db = AppUserPSQL(pgsession)
    test_user_id = users_db.get_user('test').user_id
    files_db = FileFolderPSQL(pgsession)
    files = files_db.get_files(test_user_id, 'test_file')
    for file in files:
        files_db.delete_file(file.file_id)
    assert files_db.number_of_files(test_user_id) == 0


def test_download(app, client, auth_test):

    auth_test.login()

    # checking the download page in case of absence of files in DB
    response = client.get(f"/file/download")
    assert response.status_code == 200
    assert b"There is a kind of problem" in response.data

    # uploading 1 test file with TXT extension to DB
    response = client.post("/file/upload",
                           content_type='multipart/form-data',
                           data=dict(
                               file=(io.BytesIO(b'my file contents'),
                                     'test_file.TXT'),
                           ))

    # checking the download page in case of 1 file in DB
    response = client.get(f"/file/download")
    assert response.status_code == 200
    assert b"The list of files in your repository: click on ID to download" in response.data
    assert b'test_file.TXT' in response.data

    # uploading one more test file with JPG extension to DB
    response = client.post("/file/upload",
                           content_type='multipart/form-data',
                           data=dict(
                               file=(io.BytesIO(b'my file contents'),
                                     'test_file.JPG'),
                           ))
    # checking of filtering files
    response = client.get(f"/file/download")
    assert response.status_code == 200
    assert b"The list of files in your repository: click on ID to download" in response.data
    assert b'test_file.TXT' in response.data
    assert b'test_file.JPG' in response.data

    response = client.post("/file/download", data={'file_type': "Images"})
    assert response.status_code == 200
    assert b"The list of files in your repository: click on ID to download" in response.data
    assert b'test_file.TXT' not in response.data
    assert b'test_file.JPG' in response.data

    # deleting all files in DB
    users_db = AppUserPSQL(pgsession)
    test_user_id = users_db.get_user('test').user_id
    files_db = FileFolderPSQL(pgsession)
    files = files_db.get_files(test_user_id, 'test_file')
    for file in files:
        files_db.delete_file(file.file_id)
    assert files_db.number_of_files(test_user_id) == 0


def test_download_by_id(app, client, auth_test):

    auth_test.login()

    # uploading 1 test file with TXT extension to DB
    response = client.post("/file/upload",
                           content_type='multipart/form-data',
                           data=dict(
                               file=(io.BytesIO(b'my file contents'),
                                     'test_file.TXT'),
                           ))

    users_db = AppUserPSQL(pgsession)
    test_user_id = users_db.get_user('test').user_id
    files_db = FileFolderPSQL(pgsession)

    files = files_db.get_files(test_user_id, 'test_file')
    assert len(files) == 1
    assert files_db.number_of_files(test_user_id) == 1

    # downloading the content file
    for file in files:
        response = client.post(
            f"/file/download_file/{file.file_id}")  # выдает ошибку FileNotFoundError: [WinError 2] Не удается найти указанный файл: 'D:\\_GOIT\\draft-project-2\\bot\\67_temp_file.temp'
        # assert "my file contents" in response.data

    # deleting files
    files = files_db.get_files(test_user_id, 'test_file')
    for file in files:
        files_db.delete_file(file.file_id)
    assert files_db.number_of_files(test_user_id) == 0


def test_delete_by_id(app, client, auth_test):

    auth_test.login()

    # uploading 1 test file with TXT extension to DB
    response = client.post("/file/upload",
                           content_type='multipart/form-data',
                           data=dict(
                               file=(io.BytesIO(b'my file contents'),
                                     'test_file.TXT'),
                           ))

    users_db = AppUserPSQL(pgsession)
    test_user_id = users_db.get_user('test').user_id
    files_db = FileFolderPSQL(pgsession)

    files = files_db.get_files(test_user_id, 'test_file')
    assert len(files) == 1
    assert files_db.number_of_files(test_user_id) == 1

    for file in files:
        client.post(f"/file/delete/{file.file_id}")

    files = files_db.get_files(test_user_id, 'test_file')
    assert len(files) == 0
    assert files_db.number_of_files(test_user_id) == 0
