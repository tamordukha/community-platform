from flask import Flask, Blueprint, request, redirect, url_for, session, abort, jsonify
from models.mute import mute_user, unmute_user, get_mute, is_muted, get_filter_mutes
from models.user import get_user_by_id

from utils.permissions import can_manage
from utils.validators import is_valid_reason, is_valid_duration

from datetime import datetime, timedelta, UTC


mutes_bp = Blueprint("mutes", __name__)

@mutes_bp.route("/mute/<int:profile_user_id>", methods=["POST"])
def mute(profile_user_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    current_user = get_user_by_id(session["user_id"])
    profile_user = get_user_by_id(profile_user_id)
    reason = request.form.get("mute_reason")
    duration = request.form.get("mute_duration")  # "24h", "7d"

    if not is_valid_duration(duration, hours):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Duration must use a number followed by a unit, e.g., '24h' or '7d'"}), 400
        abort(400)

    hours = int(duration[:-1]) * (24 if duration.endswith('d') else 1)

    if hours < 1 or hours > 720:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Duration must be 1 hour to 30 days"}), 400
        abort(400)
    
    expires_at = datetime.now(UTC) + timedelta(hours=hours)

    if profile_user is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User not found"}), 404
        abort(404)

    if not can_manage(current_user, profile_user):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant mute user"}), 403
        abort(403)

    if not is_valid_reason(reason):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Reason must be 4-200 characters"}), 400
        abort(400)

    if is_muted(profile_user.id):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User is already muted"}), 400
        abort(400)
    
    mute_user(profile_user.id, current_user.id, reason, expires_at)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"muted": True})
    
    return redirect(url_for("profiles.profile", profile_user_id=profile_user_id))


@mutes_bp.route("/unmute/<int:mute_id>", methods=["POST"])
def unmute(mute_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    mute = get_mute(mute_id)

    if mute is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Mute is not found"}), 404
        abort(404)

    if not mute.is_active:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Mute is not active"}), 400
        abort(400)

    current_user = get_user_by_id(session["user_id"])
    profile_user = get_user_by_id(mute.user_id)

    if not profile_user or not current_user:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User not found"}), 404
        abort(404)

    if can_manage(current_user, profile_user):
        unmute_user(mute_id)
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant mute user"}), 403
        abort(403)
        
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"unmuted": True})
    
    return redirect(url_for("moderation.moderation_page"))
    