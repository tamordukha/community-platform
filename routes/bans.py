from flask import Flask, Blueprint, request, redirect, url_for, session, abort, jsonify
from models.ban import ban_user, unban_user, get_ban, is_banned, get_filter_bans
from models.user import get_user_by_id

from utils.permissions import can_manage
from utils.validators import is_valid_reason

bans_bp = Blueprint("bans", __name__)

@bans_bp.route("/ban/<int:profile_user_id>", methods=["POST"])
def ban(profile_user_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    current_user = get_user_by_id(session["user_id"])
    profile_user = get_user_by_id(profile_user_id)
    reason = request.form.get("ban_reason")

    if not current_user or not profile_user:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User not found"}), 404
        abort(404)

    if not can_manage(current_user, profile_user):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant ban user"}), 403
        abort(403)

    if not is_valid_reason(reason):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Reason must be 4-200 characters"}), 400
        abort(400)

    if is_banned(profile_user.id):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User is already banned"}), 400
        abort(400)
    
    ban_user(profile_user.id, current_user.id, reason)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"banned": True})
    
    return redirect(url_for("profiles.profile", profile_user_id=profile_user_id))


@bans_bp.route("/unban/<int:ban_id>", methods=["POST"])
def unban(ban_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    ban = get_ban(ban_id)

    if ban is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Ban not found"}), 404
        abort(404)

    if ban.is_active == False:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Ban is not active"}), 400
        abort(400)

    current_user = get_user_by_id(session["user_id"])
    profile_user = get_user_by_id(ban.user_id)

    if not profile_user or not current_user:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User not found"}), 404
        abort(404)

    if can_manage(current_user, profile_user):
        unban_user(ban_id)
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant ban user"}), 403
        abort(403)
        
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"unbanned": True})
    
    return redirect(url_for("moderation.moderation_page"))
    