from app import app
from database.db import db
from config import Config

from models import *

'''
follows tests:

follow
- test_follow_user_success
- test_follow_user_unauthorized
- test_follow_user_missing_user
- test_cannot_follow_yourself

unfollow
- test_unfollow_user_success

AJAX
- test_follow_user_ajax_success
- test_follow_user_ajax_unauthorized
- test_follow_user_ajax_missing_user
- test_ajax_cannot_follow_yourself
'''

# Follow

def test_follow_user_success(auth_client, auth_foreign_client, follow_user):
    response = follow_user(auth_client, 2)
    
    assert response.status_code == 302
    
    with app.app_context():
        follow = db.session.query(Follow).filter_by(follower_id=1, following_id=2).first()
        assert follow is not None


def test_follow_user_unauthorized(client, auth_client, follow_user):
    response = follow_user(client, 2)
    
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"
    
    with app.app_context():
        follow = db.session.query(Follow).filter_by(follower_id=1, following_id=2).first()
        assert follow is None


def test_follow_user_missing_user(auth_client, follow_user):
    response = follow_user(auth_client, 999)
    
    assert response.status_code == 404
    
    with app.app_context():
        follow = db.session.query(Follow).filter_by(follower_id=1, following_id=999).first()
        assert follow is None


def test_cannot_follow_yourself(auth_client, follow_user):
    response = follow_user(auth_client, 1)
    
    assert response.status_code == 302
    
    with app.app_context():
        follow = db.session.query(Follow).filter_by(follower_id=1, following_id=1).first()
        assert follow is None


# Unfollow

def test_unfollow_user_success(auth_client, auth_foreign_client, follow_user):
    follow_user(auth_client, 2)

    with app.app_context():
        follow = db.session.query(Follow).filter_by(follower_id=1, following_id=2).first()
        assert follow is not None

    response = follow_user(auth_client,2)
    
    assert response.status_code == 302
    
    with app.app_context():
        follow = db.session.query(Follow).filter_by(follower_id=1, following_id=2).first()
        assert follow is None


# AJAX

def test_follow_user_ajax_success(auth_client, auth_foreign_client):
    response = auth_client.post(
        "/follow/2",
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    
    assert response.status_code == 200
    assert response.json == {"following": True}
    
    with app.app_context():
        follow = db.session.query(Follow).filter_by(follower_id=1, following_id=2).first()
        assert follow is not None


def test_follow_user_ajax_unauthorized(client, auth_client):
    response = client.post(
        "/follow/2",
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}
    
    with app.app_context():
        follow = db.session.query(Follow).filter_by(follower_id=1, following_id=2).first()
        assert follow is None


def test_follow_user_ajax_missing_user(auth_client):
    response = auth_client.post(
        "/follow/999",
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    
    assert response.status_code == 404
    assert response.json == {"error": "User not found"}
    
    with app.app_context():
        follow = db.session.query(Follow).filter_by(follower_id=1, following_id=999).first()
        assert follow is None


def test_ajax_cannot_follow_yourself(auth_client):
    response = auth_client.post(
        "/follow/1",
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    
    assert response.status_code == 400
    assert response.json == {"error": "Cannot follow yourself"}
    
    with app.app_context():
        follow = db.session.query(Follow).filter_by(follower_id=1, following_id=1).first()
        assert follow is None
