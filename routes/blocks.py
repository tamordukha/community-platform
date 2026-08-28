from flask import Flask, Blueprint, request, redirect, url_for, session, abort, jsonify
from models.block import Block, toggle_block, is_blocked
from models.user import get_user_by_id
from models.public import get_public_by_tag, unfollow_public
from utils.permissions import can_block_user

blocks_bp = Blueprint("blocks", __name__)


# user -> user
@blocks_bp.route("/toggle_block/user/<int:profile_user_id>", methods=["POST"])
def toggle_block_user(profile_user_id):
    user_id = session.get("user_id")
    if not user_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    current_user = get_user_by_id(user_id)
    user = get_user_by_id(profile_user_id)

    if not current_user or not user:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User not found"}), 404
        return abort(404)

    if can_block_user(current_user, user):
        toggle_block("user", current_user.id, "user", user.id)
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant block user"}), 403
        return abort(403)

    blocked = is_blocked("user", current_user.id, "user", user.id)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"blocked": blocked})
    
    return redirect(url_for("profiles.profile", profile_user_id=profile_user_id))

# user -> public
@blocks_bp.route("/toggle_block/publics/<tag>", methods=["POST"])
def toggle_block_public(tag):
    user_id = session.get("user_id")
    if not user_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    current_user = get_user_by_id(user_id)
    public = get_public_by_tag(tag)

    if not current_user:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User not found"}), 404
        return abort(404)
    
    if not public:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Public not found"}), 404
        return abort(404)

    toggle_block("user", current_user.id, "public", public.id)
    unfollow_public(current_user.id, public.id)

    blocked = is_blocked("user", current_user.id, "public", public.id)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"blocked": blocked})
    
    return redirect(url_for("publics.show_public", tag=tag))

# public -> user
@blocks_bp.route("/toggle_block/publics/<tag>/user/<int:profile_user_id>", methods=["POST"])
def toggle_block_member(tag, profile_user_id):
    user_id = session.get("user_id")
    if not user_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    current_user = get_user_by_id(user_id)
    user = get_user_by_id(profile_user_id)
    public = get_public_by_tag(tag)

    if not current_user or not user:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User not found"}), 404
        return abort(404)

    if not public:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Public not found"}), 404
        return abort(404)

    toggle_block("public", public.id, "user", user.id)
    unfollow_public(user.id, public.id)

    blocked = is_blocked("public", public.id, "user", user.id)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"blocked": blocked})
    
    return redirect(url_for("publics.show_public_followers", tag=tag))