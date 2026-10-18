from app import app
from database.db import db

from models import *
from models.ban import ban_user

"""
test bans

ban

- test_ban_success
- test_cannot_ban_unauthorized
- test_cannot_ban_himself
- test_cannot_ban_missing_user
- test_cannot_ban_invalid_reason
- test_cannot_ban_already_banned_user


unban

- test_unban_success
- test_unban_unauthorized
- test_cannot_unban_missing_ban
- test_cannot_unban_already_unbanned_user


AJAX

- test_ajax_ban_success
- test_ajax_cannot_ban_unauthorized
- test_ajax_cannot_ban_missing_user

- test_ajax_unban_success
- test_ajax_cannot_unban_unauthorized
- test_ajax_cannot_unban_missing_ban


permissions

- test_user_cannot_ban
- test_moderator_cannot_ban_admin
- test_admin_can_ban_moderator

- test_user_cannot_unban
- test_moderator_cannot_unban_admin
- test_admin_can_unban_moderator

"""


# === BAN ==============================================

def test_ban_success(auth_mod_client, auth_foreign_client, ban):
    response = ban(auth_mod_client)

    assert response.status_code == 302

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is not None
    
def test_cannot_ban_unauthorized(client, auth_foreign_client, ban):
    response = ban(client)

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is None

    
def test_cannot_ban_himself(auth_mod_client, ban):
    response = ban(auth_mod_client, 1)

    assert response.status_code == 403

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is None

    
def test_cannot_ban_missing_user(auth_mod_client, ban):
    response = ban(auth_mod_client)

    assert response.status_code == 404

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is None

    
def test_cannot_ban_invalid_reason(auth_mod_client, auth_foreign_client, ban):
    response = ban(auth_mod_client, reason="a")

    assert response.status_code == 400

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is None

    
def test_cannot_ban_already_banned_user(auth_mod_client, auth_foreign_client, ban):
    ban(auth_mod_client)

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is not None

    response = ban(auth_mod_client)

    assert response.status_code == 400

    with app.app_context():
        ban_obj = db.session.get(Ban, 2)
        assert ban_obj is None


# === UNBAN ==============================================

def test_unban_success(auth_mod_client, auth_foreign_client, ban, unban):
    ban(auth_mod_client)

    response = unban(auth_mod_client)

    assert response.status_code == 302

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is not None and not ban_obj.is_active
    

def test_unban_unauthorized(auth_mod_client, auth_foreign_client, client, ban, unban):
    ban(auth_mod_client)

    response = unban(client)

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is not None and ban_obj.is_active


def test_cannot_unban_missing_ban(auth_mod_client, auth_foreign_client, unban):
    response = unban(auth_mod_client)
    assert response.status_code == 404


def test_cannot_unban_already_unbanned_user(auth_mod_client, auth_foreign_client, ban, unban):
    ban(auth_mod_client)
    unban(auth_mod_client)

    response = unban(auth_mod_client)

    assert response.status_code == 400


# === AJAX ==============================================

# Ban

def test_ajax_ban_success(auth_mod_client, auth_foreign_client):
    response = auth_mod_client.post(
            f"/ban/2",
            data={"ban_reason": "reason"},
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
    
    assert response.status_code == 200

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is not None


def test_ajax_cannot_ban_unauthorized(client, auth_foreign_client):
    response = client.post(
            f"/ban/2",
            data={"ban_reason": "reason"},
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
    
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}


def test_ajax_cannot_ban_missing_user(auth_mod_client, ban):
    response = auth_mod_client.post(
            f"/ban/2",
            data={"ban_reason": "reason"},
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
    
    assert response.status_code == 404
    assert response.json == {"error": "User not found"}


# Unban

def test_ajax_unban_success(auth_mod_client, auth_foreign_client, ban):
    ban(auth_mod_client)

    response = auth_mod_client.post(
            f"/unban/1",
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
    
    assert response.status_code == 200

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is not None and not ban_obj.is_active


def test_ajax_cannot_unban_authorized(auth_mod_client, auth_foreign_client, client, ban):
    ban(auth_mod_client)

    response = client.post(
            f"/unban/1",
            headers={"X-Requested-With": "XMLHttpRequest"}
        )

    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}


def test_ajax_cannot_unban_missing_ban(auth_mod_client, auth_foreign_client, unban):
    response = auth_mod_client.post(
            f"/unban/1",
            headers={"X-Requested-With": "XMLHttpRequest"}
        )

    assert response.status_code == 404
    assert response.json == {"error": "Ban not found"}



# === PERMISSIONS ==============================================

# Ban

def test_user_cannot_ban(auth_client, auth_foreign_client, ban):
    response = ban(auth_client)
    assert response.status_code == 403


def test_moderator_cannot_ban_admin(auth_mod_client, auth_admin_client, ban):
    response = ban(auth_mod_client)
    assert response.status_code == 403


def test_admin_can_ban_moderator(auth_admin_client, auth_mod_client, ban):
    response = ban(auth_admin_client)

    assert response.status_code == 302

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is not None and ban_obj.is_active





# Unban

def test_user_cannot_unban(auth_mod_client, auth_foreign_client, auth_client, ban, unban):
    ban(auth_mod_client)
    response = unban(auth_client)

    assert response.status_code == 403
    

def test_moderator_cannot_unban_admin(auth_mod_client, auth_admin_client, unban):
    with app.app_context():
        ban_user(2, 1, "reason")

    response = unban(auth_mod_client)
    assert response.status_code == 403


def test_admin_can_unban_moderator(auth_admin_client, auth_mod_client, ban, unban):
    ban(auth_admin_client)

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is not None and ban_obj.is_active

    response = unban(auth_admin_client)

    assert response.status_code == 302

    with app.app_context():
        ban_obj = db.session.get(Ban, 1)
        assert ban_obj is not None and not ban_obj.is_active


