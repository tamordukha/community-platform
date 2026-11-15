from flask import Flask, Blueprint, request, redirect, url_for, session, abort, jsonify
from models.report import add_report, dismiss_report, get_report, is_reported, get_filter_reports, get_target
from models.user import get_user_by_id
from models.post import get_post
from models.comment import get_comment
from models.reply import get_reply
from models.public import get_public_by_id, get_member

from utils.permissions import is_moderator
from utils.validators import is_valid_reason

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/report/<string:source_type>/<int:source_id>", methods=["POST"])
def report(source_type, source_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    current_user = get_user_by_id(session["user_id"])
    reason = request.form.get("report_reason")

    if not is_valid_reason(reason):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Reason must be 4-200 characters"}), 400
        abort(400)
    
    if len(get_filter_reports(reporter_id=current_user.id)) >= 5:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You have reached the maximum of 5 reports"}), 403
        abort(403)

    content = None
    post = None
    target = None
    redirect_to = request.form.get("redirect_to", "feed")

    fetch_functions = {
        "post": get_post,
        "comment": get_comment,
        "reply": get_reply
    }

    if source_type in ("user", "public"):
        target = get_target(source_type, source_id)

    else:
        fetch_content = fetch_functions.get(source_type)
        if not fetch_content:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"error": "Invalid source_type"}), 400
            abort(400)

        content = fetch_content(source_id)
        if not content:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"error": "Source object not found"}), 404
            abort(404)

        if content.author_id:
            target = get_target("user", content.author_id)

        post = content if source_type == "post" else get_post(content.post_id)
        
        if post.public_id:
            target = get_target("public", post.public_id)
    
    target_obj, target_type = target

    if not target_obj:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Target object not found"}), 404
        abort(404)

    if target_type == "user" and current_user.id == target_obj.id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User cannot report himself"}), 403
        abort(403)

    if content and current_user.id == content.author_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User cannot report his own post/content"}), 403
        abort(403)

    if is_reported(source_id, source_type, current_user.id):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User/public/post/content is already reported"}), 400
        abort(400)
 
    add_report(source_id, source_type ,target_obj.id, target_type, current_user.id, reason)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"reported": True})
    
    if redirect_to == "profile":
        return redirect(url_for("profiles.profile", profile_user_id = target_obj.id))

    if redirect_to == "public":
        return redirect(url_for("publics.show_public", tag = target_obj.tag))

    if redirect_to == "post":
        return redirect(url_for("posts.show_post", post_id = post.id))

    return redirect(url_for("posts.feed"))


@reports_bp.route("/resolve_report/<int:report_id>", methods=["POST"])
def resolve_report(report_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    current_user = get_user_by_id(session["user_id"])

    if not is_moderator(current_user):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant dismiss report"}), 403
        abort(403)

    report = get_report(report_id)

    if report is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Report is not found"}), 404
        abort(404)

    if not report.is_pending:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Report is already dismissed"}), 400
        abort(400)

    target_obj, target_type = get_target(report.target_type, report.target_id)

    if not target_obj:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "target object not found"}), 404
        abort(404)

    if current_user.id == report.reporter_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant dismiss your own report"}), 403
        abort(403)

    if target_type == "user" and current_user.id == target_obj.id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant dismiss report against yourself"}), 403
        abort(403)

    member = get_member(current_user.id, target_obj.id) if target_type == "public" else None

    if member and member.role in ("admin", "owner"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant dismiss report against your own public"}), 403
        abort(403)
    
    dismiss_report(report_id)
        
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"report dismissed": True})
    
    return redirect(url_for("moderation.moderation_page"))
    