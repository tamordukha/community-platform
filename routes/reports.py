from flask import Flask, Blueprint, request, redirect, url_for, session, abort, jsonify
from models.report import add_report, dismiss_report, get_report, is_reported, get_filter_reports
from models.user import get_user_by_id
from models.post import get_post
from models.comment import get_comment
from models.reply import get_reply
from models.public import get_public_by_id, get_member

from utils.permissions import is_moderator
from utils.validators import is_valid_reason

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/report/<string:target_type>/<int:target_id>", methods=["POST"])
def report(target_type, target_id):
    # target_type: "user" / "post" / "comment" / "reply"
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    current_user = get_user_by_id(session["user_id"])
    target_obj = None
    target_kind = None
    post = get_post(target_id) if target_type == "post" else None
    reason = request.form.get("report_reason")
    redirect_to = request.form.get("redirect_to", "feed")
    
    fetch_functions = {
        "post": get_post,
        "comment": get_comment,
        "reply": get_reply
    }

    if target_type == "user":
        target_obj = get_user_by_id(target_id)
        target_kind = "user"

    elif target_type == "public":
        target_obj = get_public_by_id(target_id)
        target_kind = "public"

    else:
        fetch_content = fetch_functions.get(target_type)
        if not fetch_content:
            abort(400)

        content = fetch_content(target_id)
        if not content:
            abort(404)

        post = get_post(content.post_id) if not post else post

        if fetch_content and content.author_id:
            target_obj = get_user_by_id(content.author_id)
            target_kind = "user"

        elif fetch_content and post.public_id:
            target_obj = get_public_by_id(content.public_id)
            target_kind = "public"

    if target_kind and not target_obj:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User/Public not found"}), 404
        abort(404)

    if target_kind == "user" and current_user.id == target_obj.id:
        abort(403)

    if not is_valid_reason(reason):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Reason must be 4-200 characters"}), 400
        abort(400)

    if target_kind == "user" and is_reported(target_obj.id, target_kind, current_user.id):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User is already reported"}), 400
        abort(400)

    if target_kind == "public" and is_reported(target_obj.id, target_kind, current_user.id):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Public is already reported"}), 400
        abort(400)
    
    if len(get_filter_reports(reporter_id=current_user.id)) >= 5:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You have reached the maximum of 5 reports"}), 403
        abort(403)

    add_report(target_obj.id, target_kind, current_user.id, reason)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"reported": True})
    
    if redirect_to == "profile":
        return redirect(url_for("profiles.profile", profile_user_id = target_obj.id))

    if redirect_to == "public":
        return redirect(url_for("publics.show_public", tag = target_obj.tag))

    if redirect_to == "post" and post:
        return redirect(url_for("posts.show_post", post_id = post.id))

    return redirect(url_for("posts.feed"))


@reports_bp.route("/dismiss_report/<int:report_id>", methods=["POST"])
def resolve_report(report_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    report = get_report(report_id)

    if report is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Report is not found"}), 404
        abort(404)

    if report.is_pending == False:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Report is already dismissed"}), 400
        abort(400)

    current_user = get_user_by_id(session["user_id"])
    target_obj = get_user_by_id(report.target_id) if report.target_type == "user" else get_public_by_id(report.target_id)

    if not target_obj or not current_user:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User/Public not found"}), 404
        abort(404)

    if not is_moderator(current_user):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant dismiss report"}), 403
        abort(403)

    if report.target_type == "user" and current_user.id == report.target_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant dismiss your own report"}), 403
        abort(403)

    member = get_member(current_user.id, target_obj.id) if report.target_type == "public" else None

    if member and report.target_type == "public" and current_user.id == member.user_id and member.role in ("admin", "owner"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant dismiss your own report"}), 403
        abort(403)
    
    dismiss_report(report_id)
        
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"report dismissed": True})
    
    return redirect(url_for("moderation.moderation_page"))
    