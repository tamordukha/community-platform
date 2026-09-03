from flask import Flask, Blueprint, current_app, render_template, request, redirect, url_for, session, abort, flash, jsonify
from models.user import get_user_by_id
from models.repost import is_repost, toggle_repost, get_repost_count_for_post
from models.post import get_post

reposts_bp = Blueprint('reposts', __name__)

@reposts_bp.route("/repost", methods=["POST"])
def toggle_repost_route():
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    profile_user_id = request.form.get("profile_user_id")
    redirect_to = request.form.get("redirect_to", "index")
    post_id = request.form.get("post_id")

    if not profile_user_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Missing user"}), 404
        abort(404)

    if not post_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Missing post_id"}), 400
        abort(404)

    post = get_post(post_id)

    if not post:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Post not found"}), 404
        abort(404)

    if post.author_id == user_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Cannot repost your own post"}), 400
        abort(400)

    if not post.is_public:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Cannot repost private post"}), 403
        abort(403)
    
    toggle_repost(user_id, post_id)
    reposted = is_repost(user_id, post_id)
    count = get_repost_count_for_post(post_id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"reposted": reposted, "count": count})

    if redirect_to == "profile":
        return redirect(url_for("profiles.profile", profile_user_id=profile_user_id))
    if redirect_to == "post":
        return redirect(url_for("posts.show_post", post_id=post_id))
    
    return redirect(url_for("posts.feed"))