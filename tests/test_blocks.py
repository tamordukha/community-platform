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
- test_blocked_cannot_view_post_from_public
- test_blocked_cannot_like_post
- test_blocked_cannot_repost_post
- test_blocking_cannot_like_post


Interactions (comments)

- test_blocked_cannot_comment
- test_blocked_cannot_like_comment
- test_blocked_cannot_edit_comment
- test_blocked_cannot_delete_comment

- test_blocking_cannot_comment
- test_blocking_cannot_like_comment
- test_blocking_cannot_edit_comment
- test_blocking_can_delete_comment


Interactions (replies)

- test_blocked_cannot_reply
- test_blocked_cannot_reply_to_reply
- test_blocked_cannot_like_reply
- test_blocked_cannot_edit_reply
- test_blocked_cannot_delete_reply

- test_blocking_cannot_reply
- test_blocking_cannot_reply_to_reply
- test_blocking_cannot_like_reply
- test_blocking_cannot_edit_reply
- test_blocking_can_delete_reply


Permissions (moderator)

- test_blocked_moderator_can_view_profile
- test_blocked_moderator_cannot_follow_profile

- test_blocked_moderator_can_view_public
- test_blocked_moderator_cannot_follow_public

- test_blocked_moderator_can_view_post
- test_blocked_moderator_can_view_public_post
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

- test_blocked_admin_can_view_public
- test_blocked_admin_cannot_follow_public

- test_blocked_admin_can_view_post
- test_blocked_admin_can_view_public_post
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



# === INTERACTIONS (profile) ==============================================


def test_blocked_cannot_view_profile(auth_client, auth_foreign_client, block_user):
    block_user(auth_foreign_client, 1)

    response = auth_client.get("/profiles/2")

    assert response.status_code == 200
    assert b"blocked by them" in response.data


def test_blocked_cannot_follow_profile(auth_client, auth_foreign_client, block_user, follow_user):
    block_user(auth_foreign_client, 1)

    response = follow_user(auth_client)

    assert response.status_code == 403


def test_blocked_cannot_view_profile_followers(auth_client, auth_foreign_client, block_user):
    block_user(auth_foreign_client, 1)

    response = auth_client.get("/followers/2")

    assert response.status_code == 403


def test_blocked_cannot_view_profile_followings(auth_client, auth_foreign_client, block_user):
    block_user(auth_foreign_client, 1)

    response = auth_client.get("/following/2")

    assert response.status_code == 403


def test_blocking_cannot_follow_profile(auth_client, auth_foreign_client, block_user, follow_user):
    block_user(auth_client)

    response = follow_user(auth_client)

    assert response.status_code == 403


# === INTERACTIONS (public) ==============================================

def test_blocked_cannot_view_public(auth_client, auth_foreign_client, create_public, public_block_user):
    create_public(auth_foreign_client)
    public_block_user(auth_foreign_client)

    response = auth_client.get("/publics/public_tag")

    assert response.status_code == 200
    assert b"blocked by them" in response.data


def test_blocked_cannot_follow_public(auth_client, auth_foreign_client, create_public, public_block_user, follow_public):
    create_public(auth_foreign_client)
    public_block_user(auth_foreign_client)

    response = follow_public(auth_client)

    assert response.status_code == 403


def test_blocked_cannot_view_public_followers(auth_client, auth_foreign_client, create_public, public_block_user):
    create_public(auth_foreign_client)
    public_block_user(auth_foreign_client)

    response = auth_client.get("/publics/followers/public_tag")

    assert response.status_code == 403


def test_blocking_cannot_follow_public(auth_client, auth_foreign_client, block_public, create_public, follow_public):
    create_public(auth_foreign_client)
    block_public(auth_client)

    response = follow_public(auth_client)

    assert response.status_code == 403


# === INTERACTIONS (posts) ==============================================

def test_blocked_cannot_view_post(auth_client, auth_foreign_client, block_user, create_post):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    response = auth_client.post("/post/1")

    assert response.status_code == 403


def test_blocked_cannot_like_post(auth_client, auth_foreign_client, block_user, create_post):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    response = auth_client.post(
        "/post/like",
        data={"post_id": 1}
    )

    assert response.status_code == 403


def test_blocked_cannot_repost_post(auth_client, auth_foreign_client, block_user, create_post):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    response = auth_client.post(
        "/repost",
        data={"post_id": 1}
    )

    assert response.status_code == 403


def test_blocking_cannot_like_post(auth_client, auth_foreign_client, block_user, create_post):
    create_post(auth_foreign_client)
    block_user(auth_client)

    response = auth_client.post(
        "/post/like",
        data={"post_id": 1}
    )

    assert response.status_code == 403


# === INTERACTIONS (comments) ==============================================

# Comments (blocked)

def test_blocked_cannot_comment(auth_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    response = create_comment(auth_client)

    assert response.status_code == 403


def test_blocked_cannot_like_comment(auth_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    response = auth_client.post(
        "/comment/like",
        data={"post_id": 1, "comment_id": 1}
    )

    assert response.status_code == 403


def test_blocked_cannot_edit_comment(auth_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_client)

    block_user(auth_foreign_client, 1)

    response = auth_client.post(
        "/post/1/comment/1/edit",
        data={"content": "edited"}
    )

    assert response.status_code == 403


def test_blocked_cannot_delete_comment(auth_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_client)

    block_user(auth_foreign_client, 1)

    response = auth_client.post("/post/1/comment/1/delete")

    assert response.status_code == 403


# Comments (blocking)

def test_blocking_cannot_comment(auth_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    block_user(auth_client)

    response = create_comment(auth_client)

    assert response.status_code == 403


def test_blocking_cannot_like_comment(auth_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_client)

    response = auth_client.post(
        "/comment/like",
        data={"post_id": 1, "comment_id": 1}
    )

    assert response.status_code == 403


def test_blocking_cannot_edit_comment(auth_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_client)

    block_user(auth_client)

    response = auth_client.post(
        "/post/1/comment/1/edit",
        data={"content": "edited"}
    )

    assert response.status_code == 403


def test_blocking_can_delete_comment(auth_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_client)

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment is not None

    block_user(auth_client)

    response = auth_client.post("/post/1/comment/1/delete")

    assert response.status_code == 302

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment is None


# === INTERACTIONS (replies) ==============================================

# Replies (blocked)

def test_blocked_cannot_reply(auth_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    response = create_reply(auth_client)

    assert response.status_code == 403


def test_blocked_cannot_reply_to_reply(auth_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    response = auth_client.post(
        "/post/1/comment/1/reply/1/create",
        data={"content": "reply to reply content"}
    )

    assert response.status_code == 403


def test_blocked_cannot_like_reply(auth_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    response = auth_client.post(
        "/reply/like",
        data={"post_id": 1, "reply_id": 1}
    )

    assert response.status_code == 403


def test_blocked_cannot_edit_reply(auth_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_client)

    block_user(auth_foreign_client, 1)

    response = auth_client.post(
        "/post/1/comment/1/reply/1/edit",
        data={"content": "edited"}
    )

    assert response.status_code == 403


def test_blocked_cannot_delete_reply(auth_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_client)

    block_user(auth_foreign_client, 1)

    response = auth_client.post("/post/1/comment/1/delete")

    assert response.status_code == 403


# Replies (blocking)

def test_blocking_cannot_reply(auth_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_client)

    response = create_reply(auth_client)

    assert response.status_code == 403


def test_blocking_cannot_reply_to_reply(auth_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_foreign_client)

    block_user(auth_client)

    response = auth_client.post(
        "/post/1/comment/1/reply/1/create",
        data={"content": "reply to reply content"}
    )

    assert response.status_code == 403


def test_blocking_cannot_like_reply(auth_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_foreign_client)

    block_user(auth_client)

    response = auth_client.post(
        "/reply/like",
        data={"post_id": 1, "reply_id": 1}
    )

    assert response.status_code == 403


def test_blocking_cannot_edit_reply(auth_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_client)

    block_user(auth_client)

    response = auth_client.post(
        "/post/1/comment/1/reply/1/edit",
        data={"content": "edited"}
    )

    assert response.status_code == 403


def test_blocking_cannot_delete_reply(auth_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_client)

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply is not None

    block_user(auth_client)

    response = auth_client.post("/post/1/comment/1/reply/1/delete")

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply is None



# === PERMISSIONS (moderator) ==============================================

# Profile

def test_blocked_moderator_can_view_profile(auth_mod_client, auth_foreign_client, block_user):
    block_user(auth_foreign_client, 1)

    response = auth_mod_client.get("/profiles/2")

    assert response.status_code == 200


def test_blocked_moderator_cannot_follow_profile(auth_mod_client, auth_foreign_client, follow_user, block_user):
    block_user(auth_foreign_client, 1)

    response = follow_user(auth_mod_client, 2)

    assert response.status_code == 403


# Public

def test_blocked_moderator_can_view_public(auth_mod_client, auth_foreign_client, create_public, public_block_user):
    create_public(auth_foreign_client)
    public_block_user(auth_foreign_client, profile_user_id=1)

    response = auth_mod_client.get("/publics/public_tag")

    assert response.status_code == 200


def test_blocked_moderator_cannot_follow_public(auth_mod_client, auth_foreign_client, follow_public, create_public, public_block_user):
    create_public(auth_foreign_client)
    public_block_user(auth_foreign_client, profile_user_id=1)

    response = follow_public(auth_mod_client)

    assert response.status_code == 403


# Posts

def test_blocked_moderator_can_view_post(auth_mod_client, auth_foreign_client, create_post, block_user):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    response = auth_mod_client.get("/post/1")

    assert response.status_code == 200


def test_blocked_moderator_can_view_public_post(auth_mod_client, auth_foreign_client, create_public, create_public_post, public_block_user):
    create_public(auth_foreign_client)
    create_public_post(auth_foreign_client)

    public_block_user(auth_foreign_client, profile_user_id=1)

    response = auth_mod_client.get("/post/1")

    assert response.status_code == 200


def test_blocked_moderator_can_delete_post(auth_mod_client, auth_foreign_client, create_post, block_user):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        assert post is not None

    response = auth_mod_client.post("/post/delete/1")

    assert response.status_code == 302

    with app.app_context():
        post = db.session.get(Post, 1)
        assert post is None


def test_blocked_moderator_cannot_like_post(auth_mod_client, auth_foreign_client, create_post, block_user):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    response = auth_mod_client.post(
        "/post/like",
        data={"post_id": 1}
    )

    assert response.status_code == 403


# Comments

def test_blocked_moderator_can_delete_comment(auth_mod_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        comment = db.session.get(Comment, 1)

        assert post is not None
        assert comment is not None

    response = auth_mod_client.post("/post/1/comment/1/delete")

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment is None

    assert response.status_code == 302


def test_blocked_moderator_can_hide_comment(auth_mod_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        comment = db.session.get(Comment, 1)

        assert post is not None
        assert comment is not None

    response = auth_mod_client.post("/post/1/comment/1/hide")

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment.is_hidden == 1

    assert response.status_code == 302


def test_blocked_moderator_cannot_comment(auth_mod_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    response = create_comment(auth_mod_client)

    response.status_code == 403


def test_blocked_moderator_cannot_like_comment(auth_mod_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    response = auth_mod_client.post(
        "/comment/like",
        data={"post_id": 1, "comment_id": 1}
    )

    response.status_code == 403


# Replies

def test_blocked_moderator_can_delete_reply(auth_mod_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        comment = db.session.get(Comment, 1)
        reply = db.session.get(Reply, 1)

        assert post is not None
        assert comment is not None
        assert reply is not None

    response = auth_mod_client.post("/post/1/comment/1/reply/1/delete")

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply is None


def test_blocked_moderator_can_hide_reply(auth_mod_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        comment = db.session.get(Comment, 1)
        reply = db.session.get(Reply, 1)

        assert post is not None
        assert comment is not None
        assert reply is not None

    response = auth_mod_client.post("/post/1/comment/1/reply/1/hide")

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply.is_hidden == 1


def test_blocked_moderator_cannot_reply(auth_mod_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    response = create_reply(auth_mod_client)

    response.status_code == 403


def test_blocked_moderator_cannot_like_reply(auth_mod_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    response = auth_mod_client.post(
        "/reply/like",
        data={"post_id": 1, "reply_id": 1}
    )

    response.status_code == 403



# === PERMISSIONS (admin) ==============================================

# Profile

def test_blocked_admin_can_view_profile(auth_admin_client, auth_foreign_client, block_user):
    block_user(auth_foreign_client, 1)

    response = auth_admin_client.get("/profiles/2")

    assert response.status_code == 200


def test_blocked_admin_cannot_follow_profile(auth_admin_client, auth_foreign_client, follow_user, block_user):
    block_user(auth_foreign_client, 1)

    response = follow_user(auth_admin_client, 2)

    assert response.status_code == 403


# Public

def test_blocked_admin_can_view_public(auth_admin_client, auth_foreign_client, create_public, public_block_user):
    create_public(auth_foreign_client)
    public_block_user(auth_foreign_client, profile_user_id=1)

    response = auth_admin_client.get("/publics/public_tag")

    assert response.status_code == 200


def test_blocked_admin_cannot_follow_public(auth_admin_client, auth_foreign_client, follow_public, create_public, public_block_user):
    create_public(auth_foreign_client)
    public_block_user(auth_foreign_client, profile_user_id=1)

    response = follow_public(auth_admin_client)

    assert response.status_code == 403


# Posts

def test_blocked_admin_can_view_post(auth_admin_client, auth_foreign_client, create_post, block_user):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    response = auth_admin_client.get("/post/1")

    assert response.status_code == 200


def test_blocked_admin_can_view_public_post(auth_admin_client, auth_foreign_client, create_public, create_public_post, public_block_user):
    create_public(auth_foreign_client)
    create_public_post(auth_foreign_client)

    public_block_user(auth_foreign_client, profile_user_id=1)

    response = auth_admin_client.get("/post/1")

    assert response.status_code == 200


def test_blocked_admin_can_edit_post(auth_admin_client, auth_foreign_client, create_post, block_user):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        assert post is not None

    response = auth_admin_client.post("/post/edit/1", data={
        "content": "edited post content",
        "is_public": 0,
    })

    assert response.status_code == 302

    with app.app_context():
        post = db.session.get(Post, 1)
        assert post.content == "edited post content"


def test_blocked_admin_can_delete_post(auth_admin_client, auth_foreign_client, create_post, block_user):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        assert post is not None

    response = auth_admin_client.post("/post/delete/1")

    assert response.status_code == 302

    with app.app_context():
        post = db.session.get(Post, 1)
        assert post is None


def test_blocked_admin_cannot_like_post(auth_admin_client, auth_foreign_client, create_post, block_user):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    response = auth_admin_client.post(
        "/post/like",
        data={"post_id": 1}
    )

    assert response.status_code == 403


# Comments

def test_blocked_admin_can_delete_comment(auth_admin_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        comment = db.session.get(Comment, 1)

        assert post is not None
        assert comment is not None

    response = auth_admin_client.post("/post/1/comment/1/delete")

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment is None

    assert response.status_code == 302


def test_blocked_admin_can_hide_comment(auth_admin_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        comment = db.session.get(Comment, 1)

        assert post is not None
        assert comment is not None

    response = auth_admin_client.post("/post/1/comment/1/hide")

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment.is_hidden == 1

    assert response.status_code == 302


def test_blocked_admin_can_edit_comment(auth_admin_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        comment = db.session.get(Comment, 1)

        assert post is not None
        assert comment is not None

    response = auth_admin_client.post(
        "/post/1/comment/1/edit",
        data={"content": "edited"}
    )

    with app.app_context():
        comment = db.session.get(Comment, 1)
        assert comment.content == "edited"

    assert response.status_code == 302


def test_blocked_admin_cannot_comment(auth_admin_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    block_user(auth_foreign_client, 1)

    response = create_comment(auth_admin_client)

    response.status_code == 403


def test_blocked_admin_cannot_like_comment(auth_admin_client, auth_foreign_client, create_post, create_comment, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    response = auth_admin_client.post(
        "/comment/like",
        data={"post_id": 1, "comment_id": 1}
    )

    response.status_code == 403


# Replies

def test_blocked_admin_can_delete_reply(auth_admin_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        comment = db.session.get(Comment, 1)
        reply = db.session.get(Reply, 1)

        assert post is not None
        assert comment is not None
        assert reply is not None

    response = auth_admin_client.post("/post/1/comment/1/reply/1/delete")

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply is None


def test_blocked_admin_can_hide_reply(auth_admin_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        comment = db.session.get(Comment, 1)
        reply = db.session.get(Reply, 1)

        assert post is not None
        assert comment is not None
        assert reply is not None

    response = auth_admin_client.post("/post/1/comment/1/reply/1/hide")

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply.is_hidden == 1


def test_blocked_admin_can_edit_reply(auth_admin_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    with app.app_context():
        post = db.session.get(Post, 1)
        comment = db.session.get(Comment, 1)
        reply = db.session.get(Reply, 1)

        assert post is not None
        assert comment is not None
        assert reply is not None

    response = auth_admin_client.post(
        "/post/1/comment/1/reply/1/edit",
        data={"content": "edited"}
    )

    assert response.status_code == 302

    with app.app_context():
        reply = db.session.get(Reply, 1)
        assert reply.content == "edited"


def test_blocked_admin_cannot_reply(auth_admin_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    response = create_reply(auth_admin_client)

    response.status_code == 403


def test_blocked_admin_cannot_like_reply(auth_admin_client, auth_foreign_client, create_post, create_comment, create_reply, block_user):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_foreign_client)

    block_user(auth_foreign_client, 1)

    response = auth_admin_client.post(
        "/reply/like",
        data={"post_id": 1, "reply_id": 1}
    )

    response.status_code == 403