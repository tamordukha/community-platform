from app import app
from database.db import db

from models import *
from models.mute import mute_user

"""
test mutes

mute

- test_mute_success
- test_cannot_mute_unauthorized
- test_cannot_mute_himself
- test_cannot_mute_missing_user
- test_cannot_mute_invalid_reason
- test_cannot_mute_invalid_duration
- test_cannot_mute_already_muted_user


unmute

- test_unmute_success
- test_unmute_unauthorized
- test_cannot_unmute_missing_mute
- test_cannot_unmute_already_unmuted_user


AJAX

- test_ajax_mute_success
- test_ajax_cannot_mute_unauthorized
- test_ajax_cannot_mute_missing_user

- test_ajax_unmute_success
- test_ajax_cannot_unmute_unauthorized
- test_ajax_cannot_unmute_missing_mute


permissions

- test_user_cannot_mute
- test_moderator_cannot_mute_admin
- test_admin_can_mute_moderator

- test_user_cannot_unmute
- test_moderator_cannot_unmute_admin
- test_admin_can_unmute_moderator

"""

# === MUTE ==============================================

def test_mute_success(auth_mod_client, auth_foreign_client, mute):
    response = mute(auth_mod_client)

    assert response.status_code == 302

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is not None
    
def test_cannot_mute_unauthorized(client, auth_foreign_client, mute):
    response = mute(client)

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is None

    
def test_cannot_mute_himself(auth_mod_client, mute):
    response = mute(auth_mod_client, 1)

    assert response.status_code == 403

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is None

    
def test_cannot_mute_missing_user(auth_mod_client, mute):
    response = mute(auth_mod_client)

    assert response.status_code == 404

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is None

    
def test_cannot_mute_invalid_reason(auth_mod_client, auth_foreign_client, mute):
    response = mute(auth_mod_client, reason="a")

    assert response.status_code == 400

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is None


def test_cannot_mute_invalid_duration(auth_mod_client, auth_foreign_client, mute):
    response = mute(auth_mod_client, duration="1s")
    assert response.status_code == 400

    response = mute(auth_mod_client, duration="100d")
    assert response.status_code == 400

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is None

    
def test_cannot_mute_already_muted_user(auth_mod_client, auth_foreign_client, mute):
    mute(auth_mod_client)

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is not None

    response = mute(auth_mod_client)

    assert response.status_code == 400

    with app.app_context():
        mute_obj = db.session.get(Mute, 2)
        assert mute_obj is None


# === UNMUTE ==============================================

def test_unmute_success(auth_mod_client, auth_foreign_client, mute, unmute):
    mute(auth_mod_client)

    response = unmute(auth_mod_client)

    assert response.status_code == 302

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is not None and not mute_obj.is_active
    

def test_unmute_unauthorized(auth_mod_client, auth_foreign_client, client, mute, unmute):
    mute(auth_mod_client)

    response = unmute(client)

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is not None and mute_obj.is_active


def test_cannot_unmute_missing_mute(auth_mod_client, auth_foreign_client, unmute):
    response = unmute(auth_mod_client)
    assert response.status_code == 404


def test_cannot_unmute_already_unmuted_user(auth_mod_client, auth_foreign_client, mute, unmute):
    mute(auth_mod_client)
    unmute(auth_mod_client)

    response = unmute(auth_mod_client)

    assert response.status_code == 400


# === AJAX ==============================================

# Mute

def test_ajax_mute_success(auth_mod_client, auth_foreign_client):
    response = auth_mod_client.post(
            "/mute/2",
            data={
                "mute_reason": "reason",
                "mute_duration": "24h"
            },
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
    
    assert response.status_code == 200

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is not None


def test_ajax_cannot_mute_unauthorized(client, auth_foreign_client):
    response = client.post(
            "/mute/2",
            data={
                "mute_reason": "reason",
                "mute_duration": "24h"
            },
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
    
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}


def test_ajax_cannot_mute_missing_user(auth_mod_client, mute):
    response = auth_mod_client.post(
            "/mute/2",
            data={
                "mute_reason": "reason",
                "mute_duration": "24h"
            },
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
    
    assert response.status_code == 404
    assert response.json == {"error": "User not found"}


# Unmute

def test_ajax_unmute_success(auth_mod_client, auth_foreign_client, mute):
    mute(auth_mod_client)

    response = auth_mod_client.post(
            "/unmute/1",
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
    
    assert response.status_code == 200

    with app.app_context():
        ban_obj = db.session.get(Mute, 1)
        assert ban_obj is not None and not ban_obj.is_active


def test_ajax_cannot_unmute_authorized(auth_mod_client, auth_foreign_client, client, mute):
    mute(auth_mod_client)

    response = client.post(
            "/unmute/1",
            headers={"X-Requested-With": "XMLHttpRequest"}
        )

    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}


def test_ajax_cannot_unmute_missing_mute(auth_mod_client, auth_foreign_client, unmute):
    response = auth_mod_client.post(
            "/unmute/1",
            headers={"X-Requested-With": "XMLHttpRequest"}
        )

    assert response.status_code == 404
    assert response.json == {"error": "Mute not found"}


# === PERMISSIONS ==============================================

# Mute

def test_user_cannot_mute(auth_client, auth_foreign_client, mute):
    response = mute(auth_client)
    assert response.status_code == 403


def test_moderator_cannot_mute_admin(auth_mod_client, auth_admin_client, mute):
    response = mute(auth_mod_client)
    assert response.status_code == 403


def test_admin_can_mute_moderator(auth_admin_client, auth_mod_client, mute):
    response = mute(auth_admin_client)

    assert response.status_code == 302

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is not None and mute_obj.is_active


# Unmute

def test_user_cannot_unmute(auth_mod_client, auth_foreign_client, auth_client, mute, unmute):
    mute(auth_mod_client)
    response = unmute(auth_client)

    assert response.status_code == 403
    

def test_moderator_cannot_unmute_admin(auth_mod_client, auth_admin_client, unmute):
    with app.app_context():
        mute_user(2, 1, "reason")

    response = unmute(auth_mod_client)
    assert response.status_code == 403


def test_admin_can_unmute_moderator(auth_admin_client, auth_mod_client, mute, unmute):
    mute(auth_admin_client)

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is not None and mute_obj.is_active

    response = unmute(auth_admin_client)

    assert response.status_code == 302

    with app.app_context():
        mute_obj = db.session.get(Mute, 1)
        assert mute_obj is not None and not mute_obj.is_active
