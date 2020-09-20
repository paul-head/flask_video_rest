from tests.conftest import user_headers


def test_list(video, client, user_headers):
    res = client.get("/tutorials", headers=user_headers)

    assert res.status_code == 200
    assert len(res.get_json()) == 1

    assert res.get_json()[0] == {
        "description": "This is testuser1 tutorial 3",
        "id": 1,
        "name": "Test User 1 tutorial 3",
        "user_id": 1,
    }


def test_new_video(user, client, user_headers):
    res = client.post(
        "/tutorials",
        json={
            "description": "This is testuser1 tutorial 3",
            "name": "Test User 1 tutorial 3",
        },
        headers=user_headers,
    )

    assert res.status_code == 200
    assert res.get_json()["name"] == "Test User 1 tutorial 3"
    assert res.get_json()["description"] == "This is testuser1 tutorial 3"
    assert res.get_json()["user_id"] == user.id


def test_edit_video(video, client, user_headers):
    res = client.put(
        f"/tutorials/{video.id}",
        json={
            "description": "UPD This is testuser1 tutorial 3",
            "name": "UPD Test User 1 tutorial 3",
        },
        headers=user_headers,
    )

    assert res.status_code == 200
    assert res.get_json()["name"] == "UPD Test User 1 tutorial 3"
    assert res.get_json()["description"] == "UPD This is testuser1 tutorial 3"


def test_delete_video(video, client, user_headers):
    res = client.delete(f"/tutorials/{video.id}", headers=user_headers)

    assert res.status_code == 204
