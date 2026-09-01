from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash, abort, jsonify
from models.user import User, get_user_by_id
from models.post import Post, get_post
from models.comment import Comment, get_comment
from models.reply import Reply, get_reply ,add_reply, add_reply_to_reply, update_reply, delete_reply, toggle_hide_reply
from utils.permissions import can_edit_content, can_delete_content, can_hide_content
from config import Config

replies_bp = Blueprint('replies', __name__)

@replies_bp.route("/post/<int:post_id>/comment/<int:comment_id>/reply/create", methods=["POST"])
def create_reply(post_id, comment_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    user = get_user_by_id(session.get("user_id"))
    comment = get_comment(comment_id)
    post = get_post(post_id)
    content = request.form.get("content")

    if post is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Post not found"}), 404
        abort(404)

    if comment is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Comment not found"}), 404
        abort(404)
    
    if not content or len(content) > Config.REPLY_MAX_LENGTH:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Invalid content"}), 400
        return redirect(url_for("posts.show_post", post_id=post_id))
    
    add_reply(comment_id, user.id, content)
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})
    
    return redirect(url_for("posts.show_post", post_id=post_id))

@replies_bp.route("/post/<int:post_id>/comment/<int:comment_id>/reply/<int:parent_reply_id>/create", methods=["POST"])
def create_reply_to_reply(post_id, comment_id, parent_reply_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    user = get_user_by_id(session.get("user_id"))
    comment = get_comment(comment_id)
    parent_reply = get_reply(parent_reply_id)
    content = request.form.get("content")

    if comment is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Comment not found"}), 404
        abort(404)
    if parent_reply is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "reply not found"}), 404
        abort(404)
    
    if not content or len(content) > Config.REPLY_MAX_LENGTH:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Invalid content"}), 400
        return redirect(url_for("posts.show_post", post_id=post_id))
    
    add_reply_to_reply(comment_id, parent_reply_id, user.id, content)
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})
    
    return redirect(url_for("posts.show_post", post_id=post_id))

@replies_bp.route("/post/<int:post_id>/comment/<int:comment_id>/reply/<int:reply_id>/edit", methods=["POST"])
def edit_reply(post_id, comment_id, reply_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    user = get_user_by_id(session.get("user_id"))
    comment = get_comment(comment_id)
    reply = get_reply(reply_id)
    content = request.form.get("content")

    if comment is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Comment not found"}), 404
        abort(404)
    if reply is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Reply not found"}), 404
        abort(404)
    if not can_edit_content(user, reply):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Access denied"}), 403
        abort(403)

    if not content or len(content) > Config.REPLY_MAX_LENGTH:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Invalid content"}), 400
        return redirect(url_for("posts.show_post", post_id=post_id))
    
    update_reply(reply.id, content)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})
    
    return redirect(url_for("posts.show_post", post_id=post_id))

@replies_bp.route("/post/<int:post_id>/comment/<int:comment_id>/reply/<int:reply_id>/delete", methods=["POST"])
def del_reply(post_id, comment_id, reply_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    user = get_user_by_id(session.get("user_id"))
    comment = get_comment(comment_id)
    reply = get_reply(reply_id)
    post = get_post(post_id)

    if post is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Postnot found"}), 404
        abort(404)
    if comment is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Comment not found"}), 404
        abort(404)
    if reply is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Reply not found"}), 404
        abort(404)
    if not can_delete_content(user, reply, post):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Access denied"}), 403
        abort(403)

    delete_reply(reply_id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    return redirect(url_for("posts.show_post", post_id=post_id))

@replies_bp.route("/post/<int:post_id>/comment/<int:comment_id>/reply/<int:reply_id>/hide", methods=["POST"])
def hide_reply(post_id, comment_id, reply_id):
    if not session.get("user_id"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    user = get_user_by_id(session.get("user_id"))
    post = get_post(post_id)
    comment = get_comment(comment_id)
    reply = get_reply(reply_id)

    if post is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Post not found"}), 404
        abort(404)
    if comment is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Comment not found"}), 404
        abort(404)
    if reply is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Reply not found"}), 404
        abort(404)
    if not can_hide_content(user, reply, post):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Access denied"}), 403
        abort(403)

    toggle_hide_reply(reply_id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})
    
    return redirect(url_for("posts.show_post", post_id=post_id))
