from flask import Flask, Blueprint, request, redirect, url_for, session, abort, jsonify
from models.like import (toggle_like_post, toggle_like_comment, toggle_like_reply, 
                        get_post_like, get_comment_like, get_reply_like, 
                        get_post_likes_count, get_comment_likes_count, get_reply_likes_count)

likes_bp = Blueprint('likes', __name__)

@likes_bp.route("/post/like", methods=["POST"])
def like_post():
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    redirect_to = request.form.get("redirect_to", "index")
    post_id = request.form.get("post_id")

    if not post_id:
        return jsonify({"error": "Missing post_id"}), 400

    toggle_like_post(user_id, post_id)
    like = get_post_like(user_id, post_id)
    liked = like is not None
    count = get_post_likes_count(post_id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"liked": liked, "count": count})
    
    if redirect_to == "post":
        return redirect(url_for("posts.show_post", post_id=post_id))
    return redirect(url_for("posts.index"))


@likes_bp.route("/comment/like", methods=["POST"])
def like_comment():
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    comment_id = request.form.get("comment_id")
    post_id = request.form.get("post_id")
    
    if not post_id:
        return jsonify({"error": "Missing post_id"}), 400
    if not comment_id:
        return jsonify({"error": "Missing comment_id"}), 400

    toggle_like_comment(user_id, comment_id)
    like = get_comment_like(user_id, comment_id)
    liked = like is not None
    count = get_comment_likes_count(comment_id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"liked": liked, "count": count})
    
    return redirect(url_for("posts.show_post", post_id=post_id))


@likes_bp.route("/reply/like", methods=["POST"])
def like_reply():
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    reply_id = request.form.get("reply_id")
    post_id = request.form.get("post_id")
        
    if not post_id:
        return jsonify({"error": "Missing post_id"}), 400
    if not reply_id:
        return jsonify({"error": "Missing reply_id"}), 400

    toggle_like_reply(user_id, reply_id)
    like = get_reply_like(user_id, reply_id)
    liked = like is not None
    count = get_reply_likes_count(reply_id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"liked": liked, "count": count})
    
    return redirect(url_for("posts.show_post", post_id=post_id))