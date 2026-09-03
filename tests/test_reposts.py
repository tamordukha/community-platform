from app import app
from database.db import db
from config import Config

from models import *

'''
reposts tests:

repost
- test_repost_success
- test_unrepost_success
- test_repost_unauthorized
- test_repost_missing_post
- test_cannot_repost_own_post
- test_cannot_repost_private_post

AJAX
- test_repost_ajax_success
- test_repost_ajax_unauthorized
- test_repost_ajax_missing_post
- test_ajax_cannot_repost_own_post
- test_ajax_cannot_repost_private_post
'''

def test_repost_success(auth_client, auth_foreign_client, create_post):
    create_post(auth_foreign_client)

    response = auth_client.post(
        "/repost",
        data={"post_id": 1, "profile_user_id": 2}
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with app.app_context():
        repost = db.session.query(Repost).filter_by(user_id=1, post_id=1).first()
        assert repost is not None


def test_unrepost_success(auth_client, auth_foreign_client, create_post):
    create_post(auth_foreign_client)

    for _ in range(2):
        response = auth_client.post(
            "/repost",
            data={"post_id": 1, "profile_user_id": 2}
        )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with app.app_context():
        repost = db.session.query(Repost).filter_by(user_id=1, post_id=1).first()
        assert repost is None


def test_repost_unauthorized(client, auth_foreign_client, create_post):
    create_post(auth_foreign_client)

    response = client.post(
        "/repost",
        data={"post_id": 1, "profile_user_id": 2}
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    with app.app_context():
        repost = db.session.query(Repost).filter_by(user_id=1, post_id=1).first()
        assert repost is None


def test_repost_missing_post(auth_client, auth_foreign_client):
    response = auth_client.post(
        "/repost",
        data={"post_id": 1, "profile_user_id": 2}
    )

    assert response.status_code == 404

    with app.app_context():
        repost = db.session.query(Repost).filter_by(user_id=1, post_id=1).first()
        assert repost is None


def test_cannot_repost_own_post(auth_client, create_post):
    create_post(auth_client)

    response = auth_client.post(
        "/repost",
        data={"post_id": 1, "profile_user_id": 1}
    )

    assert response.status_code == 400

    with app.app_context():
        repost = db.session.query(Repost).filter_by(user_id=1, post_id=1).first()
        assert repost is None


def test_cannot_repost_private_post(auth_client, auth_foreign_client, create_post):
    create_post(auth_foreign_client, is_public=0)

    response = auth_client.post(
        "/repost",
        data={"post_id": 1, "profile_user_id": 2}
    )

    assert response.status_code == 403

    with app.app_context():
        repost = db.session.query(Repost).filter_by(user_id=1, post_id=1).first()
        assert repost is None


# AJAX

def test_repost_ajax_success(auth_client, auth_foreign_client, create_post):
    create_post(auth_foreign_client)

    response = auth_client.post(
        "/repost",
        data={"post_id": 1, "profile_user_id": 2},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 200
    assert response.json == {"reposted": True, "count": 1}

    with app.app_context():
        repost = db.session.query(Repost).filter_by(user_id=1, post_id=1).first()
        assert repost is not None


def test_repost_ajax_unauthorized(client, auth_foreign_client, create_post):
    create_post(auth_foreign_client)

    response = client.post(
        "/repost",
        data={"post_id": 1, "profile_user_id": 2},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

    with app.app_context():
        repost = db.session.query(Repost).filter_by(user_id=1, post_id=1).first()
        assert repost is None


def test_repost_ajax_missing_post(auth_client, auth_foreign_client):
    response = auth_client.post(
        "/repost",
        data={"post_id": 1, "profile_user_id": 2},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 404
    assert response.json == {"error": "Post not found"}

    with app.app_context():
        repost = db.session.query(Repost).filter_by(user_id=1, post_id=1).first()
        assert repost is None


def test_cannot_repost_ajax_own_post(auth_client, create_post):
    create_post(auth_client)

    response = auth_client.post(
        "/repost",
        data={"post_id": 1, "profile_user_id": 1},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 400
    assert response.json == {"error": "Cannot repost your own post"}

    with app.app_context():
        repost = db.session.query(Repost).filter_by(user_id=1, post_id=1).first()
        assert repost is None


def test_cannot_repost_ajax_private_post(auth_client, auth_foreign_client, create_post):
    create_post(auth_foreign_client, is_public=0)

    response = auth_client.post(
        "/repost",
        data={"post_id": 1, "profile_user_id": 2},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 403
    assert response.json == {"error": "Cannot repost private post"}

    with app.app_context():
        repost = db.session.query(Repost).filter_by(user_id=1, post_id=1).first()
        assert repost is None