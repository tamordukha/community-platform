from app import app
from database.db import db

from models import *

'''
auth tests:

- test_register_success
- test_register_duplicate_tag
- test_register_invalid_username
- test_register_empty_tag_generates_auto
- test_register_invalid_tag
- test_register_invalid_password
- test_register_missing_fields

- test_login_success
- test_login_wrong_password
- test_login_nonexistent_tag
- test_login_banned_user
'''

# Register

def test_register_success(client):
    response = client.post("/register", data={
        "username": "username",
        "tag": "user_tag",
        "password": "Password1",
    })

    location = response.headers.get("Location")
    print("Redirect to:", location)

    assert response.status_code == 302 # редирект на ленту
    assert location == "/"


def test_register_duplicate_tag(client):
    client.post("/register", data={
        "username": "username",
        "tag": "user_tag",
        "password": "Password1",
    })

    response = client.post("/register", data={
        "username": "username",
        "tag": "user_tag",
        "password": "Password1",
    })

    assert response.status_code == 200 # остается на регистре
    assert b"Tag already taken" in response.data


def test_register_invalid_username(client):
    response = client.post("/register", data={
        "username": "a",
        "tag": "user_tag",
        "password": "Password1",
    })

    assert response.status_code == 200 # остается на регистре
    assert b"Username must be 2-20 characters" in response.data


def test_register_empty_tag_generates_auto(client):
    response = client.post("/register", data={
        "username": "username",
        "tag": "",
        "password": "Password1",
    })

    assert response.status_code == 200 # остается на регистре
    assert b"Tag generated automatically. Confirm to register" in response.data


def test_register_invalid_tag(client):
    response = client.post("/register", data={
        "username": "username",
        "tag": "1_invalid_tag?",
        "password": "Password1",
    })

    assert response.status_code == 200 # остается на регистре
    assert b"Tag must be 3-20 chars, only a-z, 0-9, _" in response.data


def test_register_invalid_password(client):
    response = client.post("/register", data={
        "username": "username",
        "tag": "user_tag",
        "password": "invalid_password",
    })

    assert response.status_code == 200 # остается на регистре
    assert b"Password must be 6-128 characters with uppercase and digit" in response.data


def test_register_invalid_password(client):
    response = client.post("/register", data={
        "username": "",
        "tag": "",
        "password": "",
    })

    assert response.status_code == 200 # остается на регистре
    assert b"Username and password are required" in response.data


# Login

def test_login_success(auth_client):
    auth_client.get("/logout")

    response = auth_client.post("/login", data={
        "tag": "user_tag",
        "password": "Password1",
    })

    location = response.headers.get("Location")
    print("Redirect to:", location)

    assert response.status_code == 302 # редирект на ленту
    assert location == "/"


def test_login_wrong_password(auth_client):
    auth_client.get("/logout")

    response = auth_client.post("/login", data={
        "tag": "user_tag",
        "password": "Wrong_Password1",
    })

    assert response.status_code == 200
    assert b"Incorrect tag or password" in response.data


def test_login_nonexistent_tag(auth_client):
    auth_client.get("/logout")

    response = auth_client.post("/login", data={
        "tag": "wrong_user_tag",
        "password": "Password1",
    })

    assert response.status_code == 200
    assert b"Incorrect tag or password" in response.data


def test_login_banned_user(auth_client):
    auth_client.get("/logout")

    with app.app_context():
        user = db.session.query(User).filter_by(tag="user_tag").first()
        user.is_banned = True
        db.session.commit()

    response = auth_client.post("/login", data={
        "tag": "user_tag",
        "password": "Password1",
    })

    assert response.status_code == 200
    assert b"User is banned" in response.data