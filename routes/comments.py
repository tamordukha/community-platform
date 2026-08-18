from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash, abort, jsonify
from models.user import User, get_user_by_id
from models.post import Post, get_post
from models.comment import Comment, get_comments_for_post, get_comment, add_comment, update_comment, delete_comment, hide_comment
from utils.permissions import can_edit_comment, can_delete_comment, can_hide_comment
from config import Config
comments_bp = Blueprint('comments', __name__)


@comments_bp.route("/post/<int:post_id>/comment/create", methods=["POST"])
def create_comment(post_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    user = get_user_by_id(session.get("user_id"))
    content = request.form.get("content")
    
    if not content or len(content) > Config.COMMENT_MAX_LENGTH:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Invalid content"}), 400
        return redirect(url_for("posts.show_post", post_id=post_id))
    
    add_comment(post_id, user.id, content)
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})
    
    return redirect(url_for("posts.show_post", post_id=post_id))

@comments_bp.route("/post/<int:post_id>/comment/<int:comment_id>/edit", methods=["POST"])
def edit_comment(post_id, comment_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    user = get_user_by_id(session.get("user_id"))
    comment = get_comment(comment_id)
    content = request.form.get("content")

    if comment is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Comment not found"}), 404
        abort(404)
    if not can_edit_comment(user, comment):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Access denied"}), 403
        abort(403)

    if not content or len(content) > Config.COMMENT_MAX_LENGTH:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Invalid content"}), 400
        return redirect(url_for("posts.show_post", post_id=post_id))
    
    update_comment(comment.id, content)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})
    
    return redirect(url_for("posts.show_post", post_id=post_id))

@comments_bp.route("/post/<int:post_id>/comment/<int:comment_id>/delete", methods=["POST"])
def del_comment(post_id, comment_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    user = get_user_by_id(session.get("user_id"))
    comment = get_comment(comment_id)

    if comment is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Comment not found"}), 404
        abort(404)
    if not can_delete_comment(user, comment):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Access denied"}), 403
        abort(403)

    delete_comment(comment_id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    return redirect(url_for("posts.show_post", post_id=post_id))

@comments_bp.route("/post/<int:post_id>/comment/<int:comment_id>/hide", methods=["POST"])
def hide_comment(post_id, comment_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    user = get_user_by_id(session.get("user_id"))
    post = get_post(post_id, user)
    comment = get_comment(comment_id)

    if post is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Post not found"}), 404
        abort(404)
    if comment is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Comment not found"}), 404
        abort(404)
    if not can_hide_comment(user, post, comment):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Access denied"}), 403
        abort(403)

    hide_comment(comment_id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})
    
    return redirect(url_for("posts.show_post", post_id=post_id))
