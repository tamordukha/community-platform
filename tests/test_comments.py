from app import app
from database.db import db
from config import Config

from models import *
from models.post import get_posts, get_post
from models.comment import get_comment, get_comments_for_post
from utils.permissions import can_view_content

'''
comments tests:

create
- test_create_comment_success
- test_create_comment_too_long
- test_create_comment_empty_content
- test_create_comment_unauthorized
- test_create_comment_missing_post

edit
- test_edit_comment_success
- test_edit_comment_too_long
- test_edit_comment_empty_content
- test_edit_comment_unauthorized
- test_edit_comment_missing_post
- test_edit_comment_missing_comment

delete
- test_delete_comment_success
- test_delete_comment_unauthorized
- test_delete_comment_missing_post
- test_delete_comment_missing_comment

hide
- test_hide_comment_success
- test_hide_comment_unauthorized
- test_hide_comment_missing_post
- test_hide_comment_missing_comment
- test_author_cannot_hide_own_comment

rules
- test_user_cannot_see_hidden_comment
- test_user_cannot_edit_comment_foreign_user
- test_user_cannot_delete_comment_foreign_user
- test_post_author_can_see_hidden_comment_foreign_user
- test_post_author_can_hide_comment_foreign_user

- test_moderator_can_see_hidden_comment_foreign_user
- test_moderator_can_delete_comment_foreign_user
- test_moderator_can_hide_comment_foreign_user
- test_moderator_cannot_edit_comment_foreign_user

- test_admin_can_edit_comment_foreign_user
'''

# Create

def test_create_comment_success(auth_client, create_comment):
    response = create_comment(auth_client)
    assert response.status_code == 302

    with app.app_context():
        assert db.session.query(Comment).count() == 1


def test_create_comment_too_long(auth_client, create_comment):
    long_content = "a" * (Config.COMMENT_MAX_LENGTH + 1)

    response = create_comment(auth_client, content=long_content)

    assert response.status_code == 302

    with app.app_context():
        assert db.session.query(Comment).count() == 0


def test_create_comment_empty_content(auth_client, create_comment):
    response = create_comment(auth_client, content="")
    assert response.status_code == 302

    with app.app_context():
        assert db.session.query(Comment).count() == 0


def test_create_comment_unauthorized(client, create_comment):
    response = create_comment(client)

    assert response.status_code == 302
    assert response.headers.get("Location") == "/login"

    with app.app_context():
        assert db.session.query(Comment).count() == 0


def test_create_comment_missing_post(auth_client):
    response = auth_client.post(
        "/post/1/comment/create",
        data={"content": "comment content",}
    )
    
    assert response.status_code == 404


# Edit

def test_edit_comment_success(auth_client, create_comment):
    create_comment(auth_client)

    response = auth_client.post(
        "/post/1/comment/1/edit",
        data={"content": "edited",}
    )

    assert response.status_code == 302

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment.content == "edited"


def test_edit_comment_too_long(auth_client, create_comment):
    long_content = "a" * (Config.COMMENT_MAX_LENGTH + 1)

    create_comment(auth_client, content="comment content")

    response = auth_client.post(
        "post/1/comment/1/edit",
        data={"content": long_content,}
    )

    assert response.status_code == 302

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment.content == "comment content"


def test_edit_comment_empty_content(auth_client, create_comment):
    create_comment(auth_client, content="comment content")

    response = auth_client.post(
        "post/1/comment/1/edit",
        data={"content": "",}
    )

    assert response.status_code == 302

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment.content == "comment content"


def test_edit_comment_unauthorized(client, auth_client, create_comment):
    create_comment(auth_client)

    response = client.post(
        "post/1/comment/1/edit",
        data={"content": "edited",}
    )

    assert response.status_code == 302
    assert response.headers.get("Location") == "/login"

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment.content == "comment content"


def test_edit_comment_missing_post(auth_client):
    response = auth_client.post(
        "/post/1/comment/1/edit",
        data={"content": "edited",}
    )

    assert response.status_code == 404


def test_edit_comment_missing_comment(auth_client, create_post):
    create_post(auth_client)

    response = auth_client.post(
        "/post/1/comment/1/edit",
        data={"content": "edited",}
    )

    assert response.status_code == 404


# Delete

def test_delete_comment_success(auth_client, create_comment):
    create_comment(auth_client)

    response = auth_client.post("/post/1/comment/1/delete")

    assert response.status_code == 302

    with app.app_context():
        assert db.session.query(Comment).count() == 0


def test_delete_comment_unauthorized(client, auth_client, create_comment):
    create_comment(auth_client)

    response = client.post("/post/1/comment/1/delete")

    assert response.status_code == 302
    assert response.headers.get("Location") == "/login"

    with app.app_context():
        assert db.session.query(Comment).count() == 1


def test_delete_comment_missing_post(auth_client):
    response = auth_client.post("/post/1/comment/1/delete")
    assert response.status_code == 404


def test_delete_comment_missing_comment(auth_client, create_post):
    create_post(auth_client)

    response = auth_client.post("/post/1/comment/1/delete")

    assert response.status_code == 404


# Hide

def test_hide_comment_success(auth_client, auth_mod_client, create_comment):
    create_comment(auth_client)

    response = auth_mod_client.post("/post/1/comment/1/hide")

    assert response.status_code == 302

    with app.app_context():
        comment = db.session.query(Comment).first()
        assert comment.is_hidden == 1


def test_hide_comment_unauthorized(client, auth_client, create_comment):
    create_comment(auth_client)

    response = client.post("/post/1/comment/1/hide")

    assert response.status_code == 302
    assert response.headers.get("Location") == "/login"

    with app.app_context():
        comment = db.session.query(Comment).first()
        assert comment.is_hidden == 0


def test_hide_comment_missing_post(auth_mod_client):
    response = auth_mod_client.post("/post/1/comment/1/hide")
    assert response.status_code == 404


def test_hide_comment_missing_comment(auth_client, auth_mod_client, create_post):
    create_post(auth_client)

    response = auth_mod_client.post("/post/1/comment/1/hide")

    assert response.status_code == 404


def test_author_cannot_hide_own_comment(auth_mod_client, create_comment):
    create_comment(auth_mod_client)

    response = auth_mod_client.post("/post/1/comment/1/hide")

    assert response.status_code == 403


# Rules (user and post author)

def test_user_cannot_see_hidden_comment(auth_client, auth_foreign_client, create_comment):
    create_comment(auth_foreign_client)

    with app.app_context():
        comment = db.session.get(Comment, 1)
        comment.is_hidden = True
        db.session.commit()

    response = auth_client.get("/post/1")

    assert response.status_code == 200
    assert b"comment content" not in response.data
    
    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment.is_hidden is True


def test_user_cannot_edit_comment_foreign_user(auth_client, auth_foreign_client, create_comment):
    create_comment(auth_foreign_client)

    response = auth_client.post(
        "/post/1/comment/1/edit",
        data={"content": "edited"}
    )

    assert response.status_code == 403

def test_user_cannot_delete_comment_foreign_user(auth_client, auth_foreign_client, create_comment):
    create_comment(auth_foreign_client)

    response = auth_client.post("/post/1/comment/1/delete")

    assert response.status_code == 403


def test_post_author_can_hide_comment_foreign_user(auth_client, auth_foreign_client, create_post):
    create_post(auth_client)

    auth_foreign_client.post(
        "/post/1/comment/create",
        data={"content": "comment content"}
    )

    response = auth_client.post("/post/1/comment/1/hide")

    assert response.status_code == 302

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment.is_hidden == True


def test_post_author_can_see_hidden_comment(auth_client, auth_foreign_client, create_post):
    create_post(auth_client)

    auth_foreign_client.post(
        "/post/1/comment/create",
        data={"content": "comment content"}
    )

    auth_client.post("/post/1/comment/1/hide")

    response = auth_client.get("/post/1")

    assert response.status_code == 200
    assert b"comment content" in response.data


# Rules (moderator)

def test_moderator_can_see_hidden_comment_foreign_user(auth_client, auth_mod_client, create_comment):
    create_comment(auth_client)

    auth_mod_client.post("/post/1/comment/1/hide")

    response = auth_mod_client.get("/post/1")

    assert response.status_code == 200
    assert b"comment content" in response.data


def test_moderator_can_delete_comment_foreign_user(auth_client, auth_mod_client, create_comment):
    create_comment(auth_client)

    response = auth_mod_client.post("/post/1/comment/1/delete")

    assert response.status_code == 302

    with app.app_context():
        assert db.session.get(Comment, 1) is None


def test_moderator_can_hide_comment_foreign_user(auth_client, auth_mod_client, create_comment):
    create_comment(auth_client)

    response = auth_mod_client.post("/post/1/comment/1/hide")

    assert response.status_code == 302

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment.is_hidden is True


def test_moderator_cannot_edit_comment_foreign_user(auth_client, auth_mod_client, create_comment):
    create_comment(auth_client)

    response = auth_mod_client.post(
        "/post/1/comment/1/edit",
        data={"content": "edited"}
    )

    assert response.status_code == 403


# Rules (admin)

def test_admin_can_edit_comment_foreign_user(auth_client, auth_admin_client, create_comment):
    create_comment(auth_client)

    response = auth_admin_client.post(
        "/post/1/comment/1/edit",
        data={"content": "edited"}
    )

    assert response.status_code == 302

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment.content == "edited"

