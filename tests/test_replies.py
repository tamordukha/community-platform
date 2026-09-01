from app import app
from database.db import db
from config import Config

from models import *

'''
replies tests:

create
- test_create_reply_success
- test_create_reply_to_reply_success
- test_create_reply_too_long
- test_create_reply_empty_content
- test_create_reply_unauthorized
- test_create_reply_missing_post
- test_create_reply_missing_comment

edit
- test_edit_reply_success
- test_edit_reply_too_long
- test_edit_reply_empty_content
- test_edit_reply_unauthorized
- test_edit_reply_missing_post
- test_edit_reply_missing_comment
- test_edit_reply_missing_reply

delete
- test_delete_reply_success
- test_delete_reply_unauthorized
- test_delete_reply_missing_post
- test_delete_reply_missing_comment
- test_delete_reply_missing_reply

hide
- test_hide_reply_success
- test_hide_reply_unauthorized
- test_hide_reply_missing_post
- test_hide_reply_missing_comment
- test_hide_reply_missing_reply
- test_author_cannot_hide_own_reply

rules
- test_user_cannot_see_hidden_reply
- test_user_cannot_edit_reply_foreign_user
- test_user_cannot_delete_reply_foreign_user
- test_post_author_can_see_hidden_reply_foreign_user
- test_post_author_can_hide_reply_foreign_user

- test_moderator_can_see_hidden_reply_foreign_user
- test_moderator_can_delete_reply_foreign_user
- test_moderator_can_hide_reply_foreign_user
- test_moderator_cannot_edit_reply_foreign_user

- test_admin_can_edit_reply_foreign_user
'''

# Create

def test_create_reply_success(auth_client, create_reply):
    response = create_reply(auth_client)
    assert response.status_code == 302

    with app.app_context():
        assert db.session.query(Reply).count() == 1


def test_create_reply_to_reply_success(auth_client, create_reply):
    create_reply(auth_client)

    response = auth_client.post(
        "/post/1/comment/1/reply/1/create",
        data={"content": "reply to reply content",}
    )

    assert response.status_code == 302

    with app.app_context():
        assert db.session.query(Reply).count() == 2


def test_create_reply_too_long(auth_client, create_reply):
    long_content = "a" * (Config.REPLY_MAX_LENGTH + 1)

    response = create_reply(auth_client, content=long_content)

    assert response.status_code == 302

    with app.app_context():
        assert db.session.query(Reply).count() == 0


def test_create_comment_empty_content(auth_client, create_reply):
    response = create_reply(auth_client, content="")
    assert response.status_code == 302

    with app.app_context():
        assert db.session.query(Reply).count() == 0


def test_create_reply_unauthorized(client, create_reply):
    response = create_reply(client)

    assert response.status_code == 302
    assert response.headers.get("Location") == "/login"

    with app.app_context():
        assert db.session.query(Reply).count() == 0


def test_create_reply_missing_post(auth_client):
    response = auth_client.post(
        "/post/1/comment/1/reply/create",
        data={"content": "reply content"}
    )
    assert response.status_code == 404


def test_create_reply_missing_comment(auth_client):
    response = auth_client.post(
        "/post/1/comment/1/reply/create",
        data={"content": "reply content",}
    )
    
    assert response.status_code == 404


# Edit

def test_edit_reply_success(auth_client, create_reply):
    create_reply(auth_client)

    response = auth_client.post(
        "/post/1/comment/1/reply/1/edit",
        data={"content": "edited",}
    )

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply.content == "edited"


def test_edit_reply_too_long(auth_client, create_reply):
    long_content = "a" * (Config.COMMENT_MAX_LENGTH + 1)

    create_reply(auth_client)

    response = auth_client.post(
        "post/1/comment/1/reply/1/edit",
        data={"content": long_content,}
    )

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply.content == "reply content"


def test_edit_reply_empty_content(auth_client, create_reply):
    create_reply(auth_client)

    response = auth_client.post(
        "post/1/comment/1/reply/1/edit",
        data={"content": "",}
    )

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply.content == "reply content"


def test_edit_reply_unauthorized(client, auth_client, create_reply):
    create_reply(auth_client)

    response = client.post(
        "post/1/comment/1/reply/1/edit",
        data={"content": "edited",}
    )

    assert response.status_code == 302
    assert response.headers.get("Location") == "/login"

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply.content == "reply content"


def test_edit_reply_missing_post(auth_client):
    response = auth_client.post(
        "/post/1/comment/1/reply/1/edit",
        data={"content": "edited",}
    )

    assert response.status_code == 404


def test_edit_reply_missing_comment(auth_client, create_post):
    create_post(auth_client)

    response = auth_client.post(
        "/post/1/comment/1/reply/1/edit",
        data={"content": "edited",}
    )

    assert response.status_code == 404


def test_edit_reply_missing_reply(auth_client, create_comment):
    create_comment(auth_client)

    response = auth_client.post(
        "/post/1/comment/1/reply/1/edit",
        data={"content": "edited",}
    )

    assert response.status_code == 404

# Delete

def test_delete_reply_success(auth_client, create_reply):
    create_reply(auth_client)

    response = auth_client.post("/post/1/comment/1/reply/1/delete")

    assert response.status_code == 302

    with app.app_context():
        assert db.session.query(Reply).count() == 0


def test_delete_reply_unauthorized(client, auth_client, create_reply):
    create_reply(auth_client)

    response = client.post("/post/1/comment/1/reply/1/delete")

    assert response.status_code == 302
    assert response.headers.get("Location") == "/login"

    with app.app_context():
        assert db.session.query(Reply).count() == 1


def test_delete_reply_missing_post(auth_client):
    response = auth_client.post("/post/1/comment/1/reply/1/delete")
    assert response.status_code == 404


def test_delete_reply_missing_comment(auth_client, create_post):
    create_post(auth_client)

    response = auth_client.post("/post/1/comment/1/reply/1/delete")

    assert response.status_code == 404


def test_delete_reply_missing_reply(auth_client, create_comment):
    create_comment(auth_client)

    response = auth_client.post("/post/1/comment/1/reply/1/delete")

    assert response.status_code == 404

# Hide

def test_hide_reply_success(auth_client, auth_mod_client, create_reply):
    create_reply(auth_client)

    response = auth_mod_client.post("/post/1/comment/1/reply/1/hide")

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.query(Reply).first()
        assert reply.is_hidden == 1


def test_hide_reply_unauthorized(client, auth_client, create_reply):
    create_reply(auth_client)

    response = client.post("/post/1/comment/1/reply/1/hide")

    assert response.status_code == 302
    assert response.headers.get("Location") == "/login"

    with app.app_context():
        reply = db.session.query(Reply).first()
        assert reply.is_hidden == 0


def test_hide_reply_missing_post(auth_mod_client):
    response = auth_mod_client.post("/post/1/comment/1/reply/1/hide")
    assert response.status_code == 404


def test_hide_reply_missing_comment(auth_client, auth_mod_client, create_post):
    create_post(auth_client)

    response = auth_mod_client.post("/post/1/comment/1/reply/1/hide")

    assert response.status_code == 404


def test_hide_reply_missing_reply(auth_client, auth_mod_client, create_comment):
    create_comment(auth_client)

    response = auth_mod_client.post("/post/1/comment/1/reply/1/hide")

    assert response.status_code == 404


def test_author_cannot_hide_own_reply(auth_mod_client, create_reply):
    create_reply(auth_mod_client)

    response = auth_mod_client.post("/post/1/comment/1/reply/1/hide")

    assert response.status_code == 403


# Rules (user and post author)

def test_user_cannot_see_hidden_reply(auth_client, auth_foreign_client, create_reply):
    create_reply(auth_foreign_client)

    with app.app_context():
        reply = db.session.get(Reply, 1)
        reply.is_hidden = True
        db.session.commit()

    response = auth_client.get("/post/1")

    assert response.status_code == 200
    assert b"reply content" not in response.data
    
    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply.is_hidden is True


def test_user_cannot_edit_reply_foreign_user(auth_client, auth_foreign_client, create_reply):
    create_reply(auth_foreign_client)

    response = auth_client.post(
        "/post/1/comment/1/reply/1/edit",
        data={"content": "edited"}
    )

    assert response.status_code == 403

def test_user_cannot_delete_reply_foreign_user(auth_client, auth_foreign_client, create_reply):
    create_reply(auth_foreign_client)

    response = auth_client.post("/post/1/comment/1/reply/1/delete")

    assert response.status_code == 403


def test_post_author_can_hide_reply_foreign_user(auth_client, auth_foreign_client, create_comment):
    create_comment(auth_client)

    auth_foreign_client.post(
        "/post/1/comment/1/reply/create",
        data={"content": "reply content"}
    )

    response = auth_client.post("/post/1/comment/1/reply/1/hide")

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply.is_hidden == True


def test_post_author_can_see_hidden_reply(auth_client, auth_foreign_client, create_comment):
    create_comment(auth_client)

    auth_foreign_client.post(
        "/post/1/comment/1/reply/create",
        data={"content": "reply content"}
    )

    auth_client.post("/post/1/comment/1/reply/hide")

    response = auth_client.get("/post/1")

    assert response.status_code == 200
    assert b"reply content" in response.data


# Rules (moderator)

def test_moderator_can_see_hidden_reply_foreign_user(auth_client, auth_mod_client, create_reply):
    create_reply(auth_client)

    auth_mod_client.post("/post/1/comment/1/reply/1/hide")

    response = auth_mod_client.get("/post/1")

    assert response.status_code == 200
    assert b"reply content" in response.data


def test_moderator_can_delete_reply_foreign_user(auth_client, auth_mod_client, create_reply):
    create_reply(auth_client)

    response = auth_mod_client.post("/post/1/comment/1/reply/1/delete")

    assert response.status_code == 302

    with app.app_context():
        assert db.session.get(Reply, 1) is None


def test_moderator_can_hide_reply_foreign_user(auth_client, auth_mod_client, create_reply):
    create_reply(auth_client)

    response = auth_mod_client.post("/post/1/comment/1/reply/1/hide")

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply.is_hidden is True


def test_moderator_cannot_edit_reply_foreign_user(auth_client, auth_mod_client, create_reply):
    create_reply(auth_client)

    response = auth_mod_client.post(
        "/post/1/comment/1/reply/1/edit",
        data={"content": "edited"}
    )

    assert response.status_code == 403


# Rules (admin)

def test_admin_can_edit_reply_foreign_user(auth_client, auth_admin_client, create_reply):
    create_reply(auth_client)

    response = auth_admin_client.post(
        "/post/1/comment/1/reply/1/edit",
        data={"content": "edited"}
    )

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply.content == "edited"

