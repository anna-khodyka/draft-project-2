def test_get_news(app, client, auth_test):
    """
    Test /contact/edit_contact handler for postgres
    :param app: fixture
    :param client: fixture
    :return:
    """
    global TEST_EDIT_DICT

    auth_test.login()

    response = client.get("/news/get_news")
    assert response.status_code == 200
    assert b"2019-nCoV" in response.data
    assert b"USD" in response.data
    assert b"Source: https://index.minfin.com.ua/ua/economy/index/inflation/"

    response = client.post("/news/get_news")
    assert response.status_code == 405
    # assert b"Here wouldn't be  method POST" in response.data
