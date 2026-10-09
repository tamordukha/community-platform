from app import app
from database.db import db
from config import Config

from models import *

"""
test blocks

block

user -> user
- test_user_block_user_success
- test_user_block_user_unauthorized
- test_user_cannot_block_himself
- test_user_block_missing_user
- test_user_block_removes_follow
- test_user_unblock_user_success

user -> public
- test_user_block_public_success
- test_user_block_public_unauthorized
- test_user_block_missing_public
- test_user_block_removes_membership
- test_user_unblock_public_success

public -> user
- test_public_block_user_success
- test_public_block_user_unauthorized
- test_public_block_missing_public
- test_public_block_missing_user
- test_public_block_removes_membership
- test_public_unblock_user_success


Interactions (profile)

- test_blocked_cannot_view_profile
- test_blocked_cannot_follow_profile
- test_blocked_cannot_view_profile_followers
- test_blocked_cannot_view_profile_followings
- test_blocking_cannot_follow_profile


Interactions (public)

- test_blocked_cannot_view_public
- test_blocked_cannot_follow_public
- test_blocked_cannot_view_public_followers
- test_blocking_cannot_follow_public


Interactions (posts)

- test_blocked_cannot_view_post
- test_blocked_cannot_like_post
- test_blocked_cannot_repost_post
- test_blocking_cannot_like_post


Interactions (comments)

- test_blocked_cannot_comment
- test_blocked_cannot_like_comment
- test_blocked_cannot_edit_comment
- test_blocked_cannot_delete_comment

- test_blocker_cannot_comment
- test_blocker_cannot_like_comment
- test_blocking_cannot_edit_comment
- test_blocking_can_delete_comment


Interactions (replies)

- test_blocked_cannot_reply
- test_blocked_cannot_like_reply
- test_blocked_cannot_edit_reply
- test_blocked_cannot_delete_reply

- test_blocking_cannot_reply
- test_blocking_cannot_like_reply
- test_blocking_cannot_edit_reply
- test_blocking_can_delete_reply


Permissions (moderator)

- test_blocked_moderator_can_view_profile
- test_blocked_moderator_cannot_follow_profile

- test_blocked_moderator_cannot_follow_public
- test_blocked_moderator_can_view_public

- test_blocked_moderator_can_view_post
- test_blocked_moderator_can_delete_post
- test_blocked_moderator_cannot_like_post

- test_blocked_moderator_can_delete_comment
- test_blocked_moderator_can_hide_comment
- test_blocked_moderator_cannot_comment
- test_blocked_moderator_cannot_like_comment

- test_blocked_moderator_can_delete_reply
- test_blocked_moderator_can_hide_reply
- test_blocked_moderator_cannot_reply
- test_blocked_moderator_cannot_like_relpy


Permissions (admin)

- test_blocked_admin_can_view_profile
- test_blocked_admin_cannot_follow_profile

- test_blocked_admin_cannot_follow_public
- test_blocked_admin_can_view_public

- test_blocked_admin_can_view_post
- test_blocked_admin_can_delete_post
- test_blocked_admin_can_edit_post
- test_blocked_admin_cannot_like_post

- test_blocked_admin_can_delete_comment
- test_blocked_admin_can_edit_comment
- test_blocked_admin_can_hide_comment
- test_blocked_admin_cannot_comment
- test_blocked_admin_cannot_like_comment

- test_blocked_admin_can_delete_reply
- test_blocked_admin_can_edit_reply
- test_blocked_admin_can_hide_reply
- test_blocked_admin_cannot_reply
- test_blocked_admin_cannot_like_relpy
"""


# === BLOCK ==============================================

# user -> user

def test_user_block_user_success(auth_client, auth_foreign_client, block_user):
    response = block_user(auth_client)

    assert response.status_code == 302

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is not None

def test_user_block_user_unauthorized(client, auth_foreign_client, block_user):
    response = block_user(client)

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is None


def test_user_cannot_block_himself(auth_client, block_user):
    response = block_user(auth_client, 1)

    assert response.status_code == 403

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is None


def test_user_block_missing_user(auth_client, block_user):
    response = block_user(auth_client, 2)

    assert response.status_code == 404

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is None


def test_user_block_removes_follow(auth_client, auth_foreign_client, follow_user, block_user):
    follow_user(auth_client)
    response = block_user(auth_client)
    
    assert response.status_code == 302

    with app.app_context():
        block = db.session.get(Block, 1)
        follow = db.session.get(Follow, 1)
        print(follow)

        assert block is not None
        assert follow is None


def test_user_unblock_user_success(auth_client, auth_foreign_client, block_user):
    block_user(auth_client)

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is not None

    response = block_user(auth_client)
    
    assert response.status_code == 302

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is None



# user -> public

def test_user_block_public_success(auth_client, auth_foreign_client, create_public, block_public):
    create_public(auth_foreign_client)
    response = block_public(auth_client)

    assert response.status_code == 302

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is not None


def test_user_block_public_unauthorized(client, auth_foreign_client, create_public, block_public):
    create_public(auth_foreign_client)
    response = block_public(client)

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is None


def test_user_block_missing_public(auth_client, auth_foreign_client, block_public):
    response = block_public(auth_client)

    assert response.status_code == 404

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is None


def test_user_block_public_removes_follow(auth_client, auth_foreign_client, create_public, follow_public, block_public):
    create_public(auth_foreign_client)
    follow_public(auth_client)
    response = block_public(auth_client)
    
    assert response.status_code == 302

    with app.app_context():
        block = db.session.get(Block, 1)
        follow = db.session.get(PublicMember, 2)

        assert block is not None
        assert follow is None


def test_user_unblock_public_success(auth_client, auth_foreign_client, create_public, block_public):
    create_public(auth_foreign_client)
    block_public(auth_client)

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is not None

    response = block_public(auth_client)

    assert response.status_code == 302

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is None



# public -> user

def test_public_block_user_success(auth_client, auth_foreign_client, create_public, public_block_user):
    create_public(auth_foreign_client)
    response = public_block_user(auth_foreign_client)

    assert response.status_code == 302

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is not None


def test_public_block_user_unauthorized(client, auth_foreign_client, create_public, public_block_user):
    create_public(auth_foreign_client)

    response = public_block_user(client, 2)

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is None


def test_public_block_missing_public(auth_client, auth_foreign_client, public_block_user):
    response = public_block_user(auth_foreign_client)

    assert response.status_code == 404

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is None


def test_public_block_user_removes_follow(auth_client, auth_foreign_client, create_public, follow_public, public_block_user):
    create_public(auth_foreign_client)
    follow_public(auth_client)
    response = public_block_user(auth_foreign_client)
    
    assert response.status_code == 302

    with app.app_context():
        block = db.session.get(Block, 1)
        follow = db.session.get(PublicMember, 2)

        assert block is not None
        assert follow is None


def test_public_unblock_user_success(auth_client, auth_foreign_client, create_public, public_block_user):
    create_public(auth_foreign_client)

    public_block_user(auth_foreign_client)

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is not None

    response = public_block_user(auth_foreign_client)

    assert response.status_code == 302

    with app.app_context():
        block = db.session.get(Block, 1)
        assert block is None

