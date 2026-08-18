from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash, abort
from models.user import User, get_user_by_id
from models.post import Post, get_posts, get_post, add_post, update_post, delete_post
from utils.permissions import can_view_post ,can_edit_post, can_delete_post
from config import Config

posts_bp = Blueprint('posts', __name__)

@posts_bp.route("/")
def index():
    if not session.get("user_id"):
        user = None
    else:
        user = get_user_by_id(session.get("user_id"))
    posts = get_posts(user)

    return render_template("posts/index.html", posts=posts, user=user, show_bottom_bar=True)

@posts_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    if not session.get("user_id"):
        user = None
    else:
        user = get_user_by_id(session.get("user_id"))
    post = get_post(post_id, user)
    if post is None:
        abort(404)
    sort = request.form.get("sort-input", "1")
    #comments = get_comments_for_post(post.id, user, sort)
    #replies = get_replies_for_post(post.id, user)

    return render_template(
        "posts/view.html", 
        post=post, user=user, sort=sort,
        can_edit_post=can_edit_post,
        can_delete_post=can_delete_post,
        )

@posts_bp.route("/post/create", methods=["GET", "POST"])
def create_post():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    user = get_user_by_id(session.get("user_id"))

    if request.method == "POST":
        content = request.form.get("content")
        is_public = int(request.form.get('is_public', 1))
        if not content:
            return render_template("posts/create.html", error="Content is required", is_public=is_public)
        if len(content) > Config.POST_MAX_LENGTH:
            return render_template("posts/create.html", error=f"Max {Config.POST_MAX_LENGTH} characters", content=content, is_public=is_public)
        add_post(user.id, content, is_public)
        return redirect(url_for("posts.index"))
    
    return render_template("posts/create.html")


@posts_bp.route("/post/edit/<int:post_id>", methods=["GET","POST"])
def edit_post(post_id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    user = get_user_by_id(session.get("user_id"))
    post = get_post(post_id, user)
    if post is None:
        abort(404)

    if request.method == "POST":
        content = request.form.get("content")
        is_public = int(request.form.get('is_public', 1))
        if not content:
            return render_template("posts/create.html", error="Content is required", is_public=is_public)
        if len(content) > Config.POST_MAX_LENGTH:
            return render_template("posts/create.html", error=f"Max {Config.POST_MAX_LENGTH} characters", content=content, is_public=is_public)
        update_post(post.id, content, is_public)
        return redirect(url_for("posts.show_post", post_id=post.id))
    
    return render_template("posts/edit.html", post=post)

@posts_bp.route("/post/delete/<int:post_id>", methods=["POST"])
def del_post(post_id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    user = get_user_by_id(session.get("user_id"))
    post = get_post(post_id, user)
    if post is None:
        abort(404)
    delete_post(post_id)
    return redirect(url_for("posts.index"))
