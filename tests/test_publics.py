from app import app
from database.db import db
from config import Config
import io

from models import *

'''
publics tests:

create
- test_create_public_success
- test_create_public_success_with_avatar
- test_create_public_success_with_banner
- test_create_public_unauthorized
- test_create_public_duplicate_tag
- test_create_public_invalid_name
- test_create_public_empty_tag_generates_auto
- test_create_public_invalid_tag
- test_create_public_invalid_avatar
- test_create_public_invalid_banner

edit
- test_edit_public_success
- test_edit_public_success_with_avatar
- test_edit_public_success_with_banner
- test_edit_public_unauthorized
- test_edit_public_duplicate_tag
- test_edit_public_invalid_name
- test_edit_public_invalid_tag
- test_edit_public_invalid_avatar
- test_edit_public_invalid_banner
- test_edit_public_missing_public

- test_avatar_public_success
- test_banner_public_success
- test_avatar_public_invalid
- test_banner_public_invalid

delete
- test_delete_public_success
- test_delete_public_unauthorized
- test_delete_public_missing_public

avatar
- test_avatar_public_success
- test_avatar_public_unauthorized
- test_avatar_public_missing_public
- test_avatar_public_missing_member
- test_avatar_public_missing_avatar
- test_avatar_public_invalid

banner
- test_banner_public_success
- test_banner_public_unauthorized
- test_banner_public_missing_public
- test_banner_public_missing_member
- test_banner_public_missing_banner
- test_banner_public_invalid

followers
- test_followers_public_success
- test_followers_public_missing_public

follow
- test_follow_public_success
- test_unfollow_public_success
- test_follow_public_unauthorized
- test_follow_public_missing_public

roles
- test_change_member_role_success
- test_change_member_role_unauthorized
- test_change_member_role_missing_post
- test_change_member_role_missing_member

kick
- test_kick_member_success
- test_kick_member_unauthorized
- test_kick_member_missing_public
- test_kick_member_missing_member

ban
- test_ban_public_success
- test_ban_public_unauthorized
- test_ban_public_missing_public


public post (create)
- test_create_public_post_success
- test_create_public_post_unauthorized
- test_create_public_post_missing_public
- test_create_public_post_missing_member
- test_create_public_post_too_long
- test_create_public_post_empty_content

public post (edit)
- test_edit_public_post_success
- test_edit_public_post_unauthorized
- test_edit_public_post_missing_member
- test_edit_public_post_missing_post
- test_edit_public_post_too_long
- test_edit_public_post_empty_content

public post (delete)
- test_delete_public_post_success
- test_delete_public_post_unauthorized
- test_delete_public_post_missing_member
- test_delete_public_post_missing_post


AJAX (follow)
- test_follow_public_ajax_success
- test_follow_public_ajax_unauthorized
- test_follow_public_ajax_missing_public

AJAX (roles)
- test_change_member_role_ajax_success
- test_change_member_role_ajax_unauthorized
- test_change_member_role_ajax_missing_public
- test_change_member_role_ajax_missing_member

AJAX (kick)
- test_kick_member_ajax_success
- test_kick_member_ajax_unauthorized
- test_kick_member_ajax_missing_public
- test_kick_member_ajax_missing_member

AJAX (ban)
- test_ban_public_ajax_success
- test_ban_public_ajax_unauthorized
- test_ban_public_ajax_missing_public


Permissions (roles)
- test_owner_can_delete_public
- test_owner_can_edit_public
- test_admin_cannot_delete_public
- test_admin_can_edit_public
- test_member_cannot_delete_public
- test_member_cannot_edit_public

Permissions (kick)
- test_admin_can_kick_member
- test_admin_cannot_kick_admin
- test_owner_can_kick_admin
- test_member_cannot_kick

Permissions (post)
- test_owner_can_create_post
- test_admin_can_create_post
- test_admin_can_edit_post
- test_admin_can_delete_post
- test_member_cannot_create_post
'''


# === CREATE ==============================================


def test_create_public_success(auth_client, create_public):
    response = create_public(auth_client, bio="public bio")

    assert response.status_code == 302

    with app.app_context():
        public = db.session.get(Public, 1)
        assert public is not None


def test_create_public_success_with_avatar(auth_client, create_public):
    with open("tests/test_images/test_image.jpg", "rb") as f:
        avatar = (f, "test_avatar.jpg")

        response = create_public(auth_client, avatar=avatar)

    assert response.status_code == 302
    assert response.headers["Location"] == "/publics/public_tag"
    
    with app.app_context():
        public = db.session.get(Public, 1)

        assert public is not None
        assert public.avatar is not None


def test_create_public_success_with_banner(auth_client, create_public):
    with open("tests/test_images/test_image.jpg", "rb") as f:
        banner = (f, "test_banner.jpg")

        response = create_public(auth_client, banner=banner)

    assert response.status_code == 302
    assert response.headers["Location"] == "/publics/public_tag"
    
    with app.app_context():
        public = db.session.get(Public, 1)

        assert public is not None
        assert public.banner is not None


def test_create_public_unauthorized(client, create_public):
    response = create_public(client)

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    with app.app_context():
        public = db.session.get(Public, 1)
        assert public is None


def test_create_public_duplicate_tag(auth_client, create_public):
    create_public(auth_client)

    response = create_public(auth_client)

    assert response.status_code == 200
    assert b"Tag already taken" in response.data

    with app.app_context():
        count = db.session.query(Public).filter_by(tag="public_tag").count()
        assert count == 1


def test_create_public_invalid_name(auth_client, create_public):
    response = create_public(auth_client, "a")

    assert response.status_code == 200
    assert b"Name must be 2-20 characters" in response.data

    with app.app_context():
        public = db.session.get(Public, 1)
        assert public is None


def test_create_public_empty_tag_generates_auto(auth_client, create_public):
    response = create_public(auth_client, tag="")


    print(response.get_data(as_text=True))
    assert response.status_code == 200
    assert b"Tag generated automatically. Confirm to create" in response.data

    with app.app_context():
        public = db.session.get(Public, 1)
        assert public is None


def test_create_public_invalid_tag(auth_client, create_public):
    response = create_public(auth_client, tag="1_invalid_tag?")

    assert response.status_code == 200
    assert b"Tag must be 3-20 chars, only a-z, 0-9, _" in response.data

    with app.app_context():
        public = db.session.get(Public, 1)
        assert public is None


def test_create_public_invalid_avatar(auth_client, create_public):
    avatar = io.BytesIO(b"fake image data"), "avatar.jpg"

    response = create_public(auth_client, avatar=avatar)

    assert response.status_code == 200
    assert b"Invalid image format" in response.data
    
    with app.app_context():
        public = db.session.get(Public, 1)
        assert public is None


def test_create_public_invalid_banner(auth_client, create_public):
    banner = io.BytesIO(b"fake image data"), "banner.jpg"

    response = create_public(auth_client, banner=banner)

    assert response.status_code == 200
    assert b"Invalid image format" in response.data
    
    with app.app_context():
        public = db.session.get(Public, 1)
        assert public is None


# === EDIT ==============================================

def test_edit_public_success(auth_client, create_public):
    create_public(auth_client)

    response = auth_client.post(
        "/publics/edit/public_tag",
        data={
            "tag": "edited_tag",
            "name": "edited name",
            "bio": "edited bio"
            }
        )

    assert response.status_code == 302

    with app.app_context():
        public = db.session.get(Public, 1)

        assert public is not None
        assert public.tag == "edited_tag"
        assert public.name == "edited name"
        assert public.bio == "edited bio"


def test_edit_public_success_with_avatar(auth_client, create_public):
    create_public(auth_client)

    with open("tests/test_images/test_image.jpg", "rb") as f:
        avatar = (f, "test_avatar.jpg")

        response = auth_client.post(
            "/publics/edit/public_tag",
            data={
                "tag": "public_tag",
                "name": "public name",
                "bio": "",
                "avatar": avatar
                }
            )

    assert response.status_code == 302
    assert response.headers["Location"] == "/publics/public_tag"
    
    with app.app_context():
        public = db.session.get(Public, 1)

        assert public is not None
        assert public.avatar is not None


def test_edit_public_success_with_banner(auth_client, create_public):
    create_public(auth_client)

    with open("tests/test_images/test_image.jpg", "rb") as f:
        banner = (f, "test_banner.jpg")

        response = auth_client.post(
            "/publics/edit/public_tag",
            data={
                "tag": "public_tag",
                "name": "public name",
                "bio": "",
                "banner": banner
                }
            )

    assert response.status_code == 302
    assert response.headers["Location"] == "/publics/public_tag"
    
    with app.app_context():
        public = db.session.get(Public, 1)

        assert public is not None
        assert public.banner is not None


def test_edit_public_unauthorized(client, auth_client, create_public):
    create_public(auth_client)

    response = client.post(
        "/publics/edit/public_tag",
        data={
            "tag": "edited_tag",
            "name": "edited name",
            "bio": "edited bio"
            }
        )

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    with app.app_context():
        public = db.session.get(Public, 1)

        assert public is not None
        assert public.tag != "edited_tag"


def test_edit_public_duplicate_tag(auth_client, create_public):
    create_public(auth_client)
    create_public(auth_client, tag="public_tag2")

    response = auth_client.post(
        "/publics/edit/public_tag2",
        data={
            "tag": "public_tag",
            "name": "edited name",
            "bio": "edited bio"
            }
        )

    assert response.status_code == 200
    assert b"Tag already taken" in response.data

    with app.app_context():
        count = db.session.query(Public).filter_by(tag="public_tag").count()
        assert count == 1


def test_edit_public_invalid_name(auth_client, create_public):
    create_public(auth_client)

    response = auth_client.post(
        "/publics/edit/public_tag",
        data={
            "tag": "edited_tag",
            "name": "a",
            "bio": "edited bio"
            }
        )

    assert response.status_code == 200
    assert b"Name must be 2-20 characters" in response.data

    with app.app_context():
        public = db.session.get(Public, 1)

        assert public is not None
        assert public.name == "public name"


def test_edit_public_invalid_tag(auth_client, create_public):
    create_public(auth_client)

    response = auth_client.post(
        "/publics/edit/public_tag",
        data={
            "tag": "1_invalid_tag?",
            "name": "edited name",
            "bio": "edited bio"
            }
        )

    assert response.status_code == 200
    assert b"Tag must be 3-20 chars, only a-z, 0-9, _" in response.data

    with app.app_context():
        public = db.session.get(Public, 1)

        assert public is not None
        assert public.tag == "public_tag"


# === DELETE ==============================================

def test_delete_public_success(auth_client, create_public):
    create_public(auth_client)

    with app.app_context():
        public = db.session.get(Public, 1)
        assert public is not None

    response = auth_client.post("/publics/delete/public_tag")

    assert response.status_code == 302

    with app.app_context():
        public = db.session.get(Public, 1)
        assert public is None


def test_delete_public_unauthorized(client, auth_client, create_public):
    create_public(auth_client)

    response = client.post("/publics/delete/public_tag")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    with app.app_context():
        public = db.session.get(Public, 1)
        assert public is not None

def test_delete_public_missing_public(auth_client):
    response = auth_client.post("/publics/delete/public_tag")

    assert response.status_code == 404

    with app.app_context():
        public = db.session.get(Public, 1)
        assert public is None


# avatar and banner

def test_avatar_public_success(auth_client, create_public):
    create_public(auth_client)

    with open("tests/test_images/test_image.jpg", "rb") as f:
        avatar = (f, "test_avatar.jpg")

        response = auth_client.post("/publics/avatar/1", data={"avatar": avatar})

    assert response.status_code == 302
    assert response.headers["Location"] == "/publics/public_tag"
    
    with app.app_context():
        public = db.session.get(Public, 1)

        assert public is not None
        assert public.avatar is not None


def test_banner_public_success(auth_client, create_public):
    create_public(auth_client)

    with open("tests/test_images/test_image.jpg", "rb") as f:
        banner = (f, "test_banner.jpg")

        response = auth_client.post("/publics/banner/1", data={"banner": banner})

    assert response.status_code == 302
    assert response.headers["Location"] == "/publics/public_tag"
    
    with app.app_context():
        public = db.session.get(Public, 1)

        assert public is not None
        assert public.banner is not None


def test_avatar_public_invalid(auth_client, create_public):
    avatar = io.BytesIO(b"fake image data"), "avatar.jpg"

    create_public(auth_client)

    response = auth_client.post("/publics/avatar/1", data={"avatar": avatar})

    assert response.status_code == 302
    
    with app.app_context():
        public = db.session.get(Public, 1)

        assert public is not None
        assert public.avatar is None


def test_banner_public_invalid(auth_client, create_public):
    banner = io.BytesIO(b"fake image data"), "banner.jpg"

    create_public(auth_client)

    response = auth_client.post("/publics/banner/1", data={"banner": banner})

    assert response.status_code == 302
    
    with app.app_context():
        public = db.session.get(Public, 1)

        assert public is not None
        assert public.banner is None