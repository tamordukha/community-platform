from app import app
from database.db import db
from config import Config

from models import *

'''
posts tests:

create
- test_create_post_success
- test_create_post_too_long
- test_create_post_empty_content
- test_create_post_unauthorized

edit
- test_edit_post_success
- test_edit_post_too_long
- test_edit_post_empty_content
- test_edit_post_unauthorized

delete
- test_delete_post_success
- test_delete_post_unauthorized

rules
- test_user_cannot_see_private_post_foreign_user
- test_user_cannot_edit_post_foreign_user
- test_user_cannot_delete_post_foreign_user

- test_moderator_can_see_private_post_foreign_user
- test_moderator_can_delete_post_foreign_user

- test_admin_can_edit_post_foreign_user
'''

# Create

def test_create_post_success(auth_client):
    response = auth_client.post("/post/create", data={
        "content": "post content",
        "is_public": 1,
    })

    assert response.status_code == 302


def test_create_post_too_long(auth_client):
    long_content = "a" * (Config.POST_MAX_LENGTH + 1)

    response = auth_client.post("/post/create", data={
        "content": long_content,
        "is_public": 1,
    })

    assert response.status_code == 200
    assert b"Max 2000 characters" in response.data


def test_create_post_empty_content(auth_client):
    response = auth_client.post("/post/create", data={
        "content": "",
        "is_public": 1,
    })

    assert response.status_code == 200
    assert b"Content is required" in response.data


def test_create_post_unauthorized(client):
    response = client.post("/post/create", data={
        "content": "",
        "is_public": 1,
    })

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


# Edit

def test_edit_post_success(auth_client):
    auth_client.post("/post/create", data={
        "content": "post content",
        "is_public": 1,
    })

    response = auth_client.post("/post/edit/1", data={
        "content": "edited post content",
        "is_public": 0,
    })

    assert response.status_code == 302


def test_edit_post_too_long(auth_client):
    long_content = "a" * (Config.POST_MAX_LENGTH + 1)

    auth_client.post("/post/create", data={
        "content": "post content",
        "is_public": 1,
    })

    response = auth_client.post("/post/edit/1", data={
        "content": long_content,
        "is_public": 0,
    })

    assert response.status_code == 200
    assert b"Max 2000 characters" in response.data


def test_edit_post_empty_content(auth_client):
    auth_client.post("/post/create", data={
        "content": "post content",
        "is_public": 1,
    })

    response = auth_client.post("/post/edit/1", data={
        "content": "",
        "is_public": 0,
    })

    assert response.status_code == 200
    assert b"Content is required" in response.data


def test_edit_post_unauthorized(client, auth_client):
    auth_client.post("/post/create", data={
        "content": "post content",
        "is_public": 1,
    })

    response = client.post("/post/edit/1", data={
        "content": "edited post content",
        "is_public": 0,
    })

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


# Delete

def test_delete_post_success(auth_client):
    auth_client.post("/post/create", data={
        "content": "post content",
        "is_public": 1,
    })

    response = auth_client.post("/post/delete/1")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_delete_post_unauthorized(client, auth_client):
    auth_client.post("/post/create", data={
        "content": "post content",
        "is_public": 1,
    })

    response = client.post("/post/delete/1")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


# Rules (user)

def test_user_cannot_see_private_post_foreign_user(auth_client, auth_foreign_client):
    auth_foreign_client.post("/post/create", data={
        "content": "post content",
        "is_public": 0,
    })

    response = auth_client.post("/post/1")

    assert response.status_code == 403


def test_user_cannot_edit_post_foreign_user(auth_client, auth_foreign_client):
    auth_foreign_client.post("/post/create", data={
        "content": "post content",
        "is_public": 1,
    })

    response = auth_client.post("/post/edit/1", data={
        "content": "edited post content",
        "is_public": 0,
    })

    assert response.status_code == 403


def test_user_cannot_delete_post_foreign_user(auth_client, auth_foreign_client):
    auth_foreign_client.post("/post/create", data={
        "content": "post content",
        "is_public": 1,
    })

    response = auth_client.post("/post/delete/1")

    assert response.status_code == 403


# Rules (moderator)

def test_moderator_can_see_private_post_foreign_user(auth_client, auth_mod_client):
    auth_client.post("/post/create", data={
        "content": "post content",
        "is_public": 0,
    })

    response = auth_mod_client.post("/post/1")

    assert response.status_code == 200

def test_moderator_can_delete_post_foreign_user(auth_client, auth_mod_client):
    auth_client.post("/post/create", data={
        "content": "post content",
        "is_public": 1,
    })

    response = auth_mod_client.post("/post/delete/1")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"


# Rules (admin)

def test_admin_can_edit_post_foreign_user(auth_client, auth_admin_client):
    auth_client.post("/post/create", data={
        "content": "post content",
        "is_public": 1,
    })

    response = auth_admin_client.post("/post/edit/1", data={
        "content": "edited post content",
        "is_public": 0,
    })
    print(auth_admin_client)

    assert response.status_code == 302
    assert response.headers["Location"] == "/post/1"