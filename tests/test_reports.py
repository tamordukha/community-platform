from app import app
from database.db import db

from models import *
from models.report import add_report

"""
test reports

REPORT

- test_cannot_report_unauthorized
- test_cannot_report_invalid_type
- test_cannot_report_invalid_reason
- test_cannot_report_with_reached_maximum
- test_cannot_report_missing_source_obj
- test_cannot_report_missing_target_obj
- test_cannot_report_reported
- test_cannot_report_himself
- test_cannot_report_his_own_content

user

- test_report_user_success
- test_report_user_post_success
- test_report_comment_success
- test_report_reply_success

public

- test_report_public_success
- test_report_public_post_success


RESOLVE REPORT

- test_resolve_report_success
- test_resolve_report_unauthorized

- test_cannot_resolve_report_missing_report
- test_cannot_resolve_already_resolved_report
- test_cannot_resolve_report_invalid_source_type
- test_cannot_resolve_report_invalid_target_type
- test_cannot_resolve_report_missing_source_obj
- test_cannot_resolve_report_missing_target_obj
- test_cannot_resolve_his_own_report
- test_cannot_resolve_report_against_yourself
- test_cannot_resolve_report_against_your_own_public


AJAX

- test_ajax_report_success
- test_ajax_cannot_report_unauthorized
- test_ajax_cannot_report_invalid_type
- test_ajax_cannot_report_missing_source_obj
- test_ajax_cannot_report_with_reached_maximum

- test_ajax_resolve_report_success
- test_ajax_cannot_resolve_report_unauthorized
- test_ajax_cannot_resolve_report_missing_report


permissions

- test_user_cannot_resolve_report
- test_moderator_can_resolve_report

"""


# === REPORT ==============================================

def test_cannot_report_unauthorized(client, auth_foreign_client, report):
    response = report(client)

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


def test_cannot_report_invalid_type(auth_client, auth_foreign_client, report):
    response = report(auth_client, source_type="invalid type")
    assert response.status_code == 400
    

def test_cannot_report_invalid_reason(auth_client, auth_foreign_client, report):
    response = report(auth_client, reason="a")
    assert response.status_code == 400


def test_cannot_report_with_reached_maximum(auth_client, auth_foreign_client, report):
    with app.app_context():
        for i in range(1, 6):
            add_report(
                source_id=i, source_type="post",
                target_id=2, target_type="user",
                reporter_id=1, reason="reason"
            )
    
    response = report(auth_client)
    assert response.status_code == 403


def test_cannot_report_missing_source_obj(auth_client, auth_foreign_client, report):
    response = report(auth_client, source_type="post", source_id=999)
    assert response.status_code == 404


def test_cannot_report_missing_target_obj(auth_client, auth_foreign_client, report):
    response = report(auth_client, source_id=999)
    assert response.status_code == 404


def test_cannot_report_reported(auth_client, auth_foreign_client, report):
    report(auth_client)
    response = report(auth_client)

    assert response.status_code == 400


def test_cannot_report_himself(auth_client, report):
    response = report(auth_client, source_id=1)
    assert response.status_code == 403


def test_cannot_report_his_own_content(auth_client, create_post, report):
    create_post(auth_client)
    response = report(auth_client, source_type="post", source_id=1)

    assert response.status_code == 403


# --- USER ----------------------------------------------

def test_report_user_success(auth_client, auth_foreign_client, report):
    response = report(auth_client)
    assert response.status_code == 302

    with app.app_context():
        db_report = db.session.get(Report, 1)
        assert db_report


def test_report_user_post_success(auth_client, auth_foreign_client, create_post, report):
    create_post(auth_foreign_client)

    response = report(auth_client, source_type="post", source_id=1, redirect_to="post")

    assert response.status_code == 302

    with app.app_context():
        db_report = db.session.get(Report, 1)
        assert db_report


def test_report_comment_success(auth_client, auth_foreign_client, create_post, create_comment, report):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)

    response = report(auth_client, source_type="comment", source_id=1, redirect_to="post")

    assert response.status_code == 302

    with app.app_context():
        db_report = db.session.get(Report, 1)
        assert db_report


def test_report_reply_success(auth_client, auth_foreign_client, create_post, create_comment, create_reply, report):
    create_post(auth_foreign_client)
    create_comment(auth_foreign_client)
    create_reply(auth_foreign_client)

    response = report(auth_client, source_type="reply", source_id=1, redirect_to="post")

    assert response.status_code == 302

    with app.app_context():
        db_report = db.session.get(Report, 1)
        assert db_report


# --- PUBLIC ----------------------------------------------

def test_report_public_success(auth_client, auth_foreign_client, create_public, report):
    create_public(auth_foreign_client)

    response = report(auth_client, source_type="public", source_id=1, redirect_to="public")

    assert response.status_code == 302

    with app.app_context():
        db_report = db.session.get(Report, 1)
        assert db_report


def test_report_public_post_success(auth_client, auth_foreign_client, create_public, create_public_post, report):
    create_public(auth_foreign_client)
    create_public_post(auth_foreign_client)

    response = report(auth_client, source_type="post", source_id=1, redirect_to="post")

    assert response.status_code == 302

    with app.app_context():
        db_report = db.session.get(Report, 1)
        assert db_report


# === RESOLVE REPORT ==============================================

def test_resolve_report_success(auth_client, auth_foreign_client, auth_mod_client, report, resolve_report):
    report(auth_client)
    response = resolve_report(auth_mod_client)

    assert response.status_code == 302

    with app.app_context():
        db_report = db.session.get(Report, 1)
        assert db_report and not db_report.is_pending


def test_resolve_report_unauthorized(client, auth_foreign_client, resolve_report):
    response = resolve_report(client)

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


def test_cannot_resolve_report_missing_report(auth_mod_client, auth_foreign_client, resolve_report):
    response = resolve_report(auth_mod_client)
    assert response.status_code == 404


def test_cannot_resolve_report_invalid_source_type(auth_client, auth_mod_client, resolve_report):
    with app.app_context():
        add_report(
            source_id=1, source_type="invalid",
            target_id=2, target_type="user",
            reporter_id=1, reason="reason"
        )
    response = resolve_report(auth_mod_client)
    assert response.status_code == 404


def test_cannot_resolve_report_invalid_target_type(auth_client, auth_mod_client, resolve_report):
    with app.app_context():
        add_report(
            source_id=2, source_type="user",
            target_id=2, target_type="invalid",
            reporter_id=1, reason="reason"
        )
    response = resolve_report(auth_mod_client)
    assert response.status_code == 404


def test_cannot_resolve_report_missing_source_obj(auth_client, auth_mod_client, auth_foreign_client, report, resolve_report):
    with app.app_context():
        add_report(
            source_id=1, source_type="post",
            target_id=3, target_type="user",
            reporter_id=1, reason="reason"
        )
    response = resolve_report(auth_mod_client)
    assert response.status_code == 404


def test_cannot_resolve_report_missing_target_obj(auth_client, auth_mod_client, report, resolve_report):
    with app.app_context():
        add_report(
            source_id=3, source_type="user",
            target_id=3, target_type="user",
            reporter_id=1, reason="reason"
        )
    response = resolve_report(auth_mod_client)
    assert response.status_code == 404


def test_cannot_resolve_already_resolved_report(auth_client, auth_foreign_client, auth_mod_client, report, resolve_report):
    report(auth_client)
    resolve_report(auth_mod_client)

    response = resolve_report(auth_mod_client)
    assert response.status_code == 409


def test_cannot_resolve_his_own_report(auth_mod_client, auth_foreign_client, report, resolve_report):
    report(auth_mod_client)
    response = resolve_report(auth_mod_client)

    assert response.status_code == 403


def test_cannot_resolve_report_against_yourself(auth_client, auth_mod_client, create_post, report, resolve_report):
    create_post(auth_mod_client)

    report(auth_client)
    report(auth_client, source_type="post", source_id=1, redirect_to="post")

    response = resolve_report(auth_mod_client)
    response_post = resolve_report(auth_mod_client, report_id=2)

    assert response.status_code == 403
    assert response_post.status_code == 403


def test_cannot_resolve_report_against_your_own_public(auth_client, auth_mod_client, create_public, create_public_post, report, resolve_report):
    create_public(auth_mod_client)
    create_public_post(auth_mod_client)

    report(auth_client, source_type="public", source_id=1, redirect_to="public")
    report(auth_client, source_type="post", source_id=1, redirect_to="post")

    response = resolve_report(auth_mod_client)
    response_post = resolve_report(auth_mod_client, report_id=2)

    assert response.status_code == 403
    assert response_post.status_code == 403


# === AJAX ==============================================

# --- REPORT --------------------------------------------

def test_ajax_report_success(auth_client, auth_foreign_client):
    response = auth_client.post(
        "/report/user/2",
        data={"report_reason": "reason"},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 200

    with app.app_context():
        db_report = db.session.get(Report, 1)
        assert db_report


def test_ajax_cannot_report_unauthorized(client, auth_foreign_client):
    response = client.post(
        "/report/user/2",
        data={"report_reason": "reason"},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}


def test_ajax_cannot_report_invalid_type(auth_client, auth_foreign_client):
    response = auth_client.post(
        "/report/invalid_type/2",
        data={"report_reason": "reason"},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 400
    assert response.json == {"error": "Invalid source type"}


def test_ajax_cannot_report_with_reached_maximum(auth_client, auth_foreign_client):
    with app.app_context():
        for i in range(1, 6):
            add_report(
                source_id=i, source_type="post",
                target_id=2, target_type="user",
                reporter_id=1, reason="reason"
            )
    
    response = auth_client.post(
        "/report/invalid_type/2",
        data={"report_reason": "reason"},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 403
    assert response.json == {"error": "You have reached the maximum of 5 reports"}


# --- RESOLVE REPORT ------------------------------------

def test_ajax_resolve_report_success(auth_client, auth_foreign_client, auth_mod_client, report):
    report(auth_client)
    response = auth_mod_client.post(
        "/resolve_report/1",
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 200

    with app.app_context():
        db_report = db.session.get(Report, 1)
        assert db_report and not db_report.is_pending


def test_ajax_cannot_resolve_report_unauthorized(client, auth_foreign_client):
    response = client.post(
        "/resolve_report/1",
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}


def test_ajax_cannot_resolve_report_missing_report(auth_mod_client):
    response = auth_mod_client.post(
        "/resolve_report/1",
        headers={"X-Requested-With": "XMLHttpRequest"}
    )

    assert response.status_code == 404
    assert response.json == {"error": "Report is not found"}


# === PERMISSIONS ==============================================

def test_user_cannot_resolve_report(auth_client, auth_foreign_client, auth_mod_client, report, resolve_report):
    report(auth_mod_client)

    response = resolve_report(auth_client)

    assert response.status_code == 403


def test_moderator_can_resolve_report(auth_client, auth_foreign_client, auth_mod_client, report, resolve_report):
    report(auth_client)

    response = resolve_report(auth_mod_client)

    assert response.status_code == 302

    with app.app_context():
        db_report = db.session.get(Report, 1)
        assert db_report and not db_report.is_pending