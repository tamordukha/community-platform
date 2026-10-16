from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash, abort, jsonify
from models.follow import follow_user, unfollow_user, is_following, get_followers, get_following
from models.user import get_user_by_id
from utils.permissions import can_view_profile, can_interact_with_profile

follows_bp = Blueprint('follows', __name__)

@follows_bp.route("/followers/<int:user_id>")
def show_followers(user_id):
    current_user_id = session.get("user_id")

    current_user = get_user_by_id(current_user_id)
    profile_user = get_user_by_id(user_id)

    if not profile_user:
        abort(404)

    if current_user and not can_view_profile(current_user, profile_user):
        abort(403)

    followers = get_followers(user_id)

    return render_template(
        "profile/followers.html",
        profile_user=profile_user,
        followers=followers
    )


@follows_bp.route("/following/<int:user_id>")
def show_following(user_id):
    current_user_id = session.get("user_id")

    current_user = get_user_by_id(current_user_id)
    profile_user = get_user_by_id(user_id)

    if not profile_user:
        abort(404)

    if current_user and not can_view_profile(current_user, profile_user):
        abort(403)

    following = get_following(user_id)

    return render_template(
        "profile/following.html",
        profile_user=profile_user,
        following=following
    )


@follows_bp.route("/follow/<int:user_id>", methods=["POST"])
def toggle_follow(user_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    follower_id = session.get("user_id")
    following_id = user_id
    
    if follower_id == following_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Cannot follow yourself"}), 400
        return redirect(url_for("profiles.profile", profile_user_id=user_id))
    
    current_user = get_user_by_id(follower_id)
    target_user = get_user_by_id(following_id)

    if target_user is None or current_user is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User not found"}), 404
        abort(404)

    if not can_interact_with_profile(current_user, target_user):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Access denied"}), 403
        abort(403)

    if is_following(follower_id, following_id):
        unfollow_user(follower_id, following_id)
        following = False
    else:
        follow_user(follower_id, following_id)
        following = True

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"following": following})
    
    return redirect(url_for("profiles.profile", profile_user_id=user_id))


