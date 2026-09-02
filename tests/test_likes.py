from app import app
from database.db import db
from config import Config

from models import *

'''
likes tests:

Success
- test_like_post_ajax_success
- test_unlike_post_ajax_success
- test_like_comment_ajax_success
- test_like_reply_ajax_success

Error
- test_like_post_ajax_unauthorized
- test_like_post_ajax_missing_post
'''

# Success

def test_like_post_ajax_success(auth_client, create_post):
    create_post(auth_client)

    response = auth_client.post(
        "/post/like",
        data={"post_id": 1},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 200
    assert response.json == {"liked": True, "count": 1}

    with app.app_context():
        like = db.session.query(PostLike).filter_by(post_id=1, user_id=1).first()
        assert like is not None


def test_unlike_post_ajax_success(auth_client, create_post):
    create_post(auth_client)
    
    for _ in range(2):
        response = auth_client.post(
            "/post/like",
            data={"post_id": 1},
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
    
    assert response.status_code == 200
    assert response.json == {"liked": False, "count": 0}
    
    with app.app_context():
        like = db.session.query(PostLike).filter_by(post_id=1, user_id=1).first()
        assert like is None


def test_like_comment_ajax_success(auth_client, create_comment):
    create_comment(auth_client)

    response = auth_client.post(
        "/comment/like",
        data={"post_id": 1, "comment_id": 1},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 200
    assert response.json == {"liked": True, "count": 1}

    with app.app_context():
        like = db.session.query(CommentLike).filter_by(comment_id=1, user_id=1).first()
        assert like is not None


def test_like_reply_ajax_success(auth_client, create_reply):
    create_reply(auth_client)

    response = auth_client.post(
        "/reply/like",
        data={"post_id": 1, "reply_id": 1},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 200
    assert response.json == {"liked": True, "count": 1}

    with app.app_context():
        like = db.session.query(ReplyLike).filter_by(reply_id=1, user_id=1).first()
        assert like is not None


# Error

def test_like_post_ajax_unauthorized(client, auth_client, create_post):
    create_post(auth_client)

    response = client.post(
        "/post/like",
        data={"post_id": 1},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

    with app.app_context():
        like = db.session.query(PostLike).filter_by(post_id=1, user_id=1).first()
        assert like is None


def test_like_post_ajax_missing_post(auth_client):
    response = auth_client.post(
        "/post/like",
        data={"post_id": 1},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 404
    assert response.json == {"error": "Post not found"}

    with app.app_context():
        like = db.session.query(PostLike).filter_by(post_id=1, user_id=1).first()
        assert like is None