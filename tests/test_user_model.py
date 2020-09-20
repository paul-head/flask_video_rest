from tests.conftest import client


def test_model(user):
    assert user.name == "testuser1"


def test_user_login(user, client):
    res = client.post(
        "/login",
        json={
            "email": user.email,
            "password": "password",
        },
    )
    assert res.status_code == 200
    assert res.get_json().get("access_token")


def test_user_reg(client):
    res = client.post(
        "/register",
        json={
            "name": "testuser1",
            "email": "testuser1@testuser.com",
            "password": "password",
        },
    )
    assert res.status_code == 200
    assert res.get_json().get("access_token")
