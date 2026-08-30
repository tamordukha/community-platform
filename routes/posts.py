from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash, abort
from models.user import get_user_by_id
from models.post import get_posts, get_post, add_post, update_post, delete_post
from models.comment import get_comments_for_post
from models.reply import get_replies_for_post
from models.public import get_public_by_tag, get_member
from utils.permissions import can_view_post, can_edit_post, can_delete_post, can_edit_public
from config import Config

posts_bp = Blueprint('posts', __name__)

@posts_bp.route("/")
def feed():
    if not session.get("user_id"):
        user = None
    else:
        user = get_user_by_id(session.get("user_id"))
    posts = get_posts(user, feed=True)

    return render_template("feed.html", posts=posts, user=user, show_bottom_bar=True)

@posts_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    if not session.get("user_id"):
        user = None
    else:
        user = get_user_by_id(session.get("user_id"))
    post = get_post(post_id, user)
    if post is None:
        abort(404)

    if not can_view_post(user, post):
        abort(403)
    
    sort = request.form.get("sort-input", "1")
    comments = get_comments_for_post(post.id, user, sort)
    replies = get_replies_for_post(post.id, user)

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
        add_post(content, is_public, author_id=user.id)
        return redirect(url_for("posts.feed"))
    
    return render_template("posts/create.html")

@posts_bp.route("/public/<tag>/post/create", methods=["GET", "POST"])
def create_public_post(tag):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    
    public = get_public_by_tag(tag)
    if not public:
        abort(404)

    member = get_member(user_id, public.id)
    if not member:
        return abort(404)

    if not can_edit_public(member, public):
        return abort(403)

    if request.method == "POST":
        content = request.form.get("content")
        if not content:
            return render_template("posts/create.html", error="Content is required", public=public)
        if len(content) > Config.POST_MAX_LENGTH:
            return render_template("posts/create.html", error=f"Max {Config.POST_MAX_LENGTH} characters", content=content, public=public)
        add_post(content, is_public=1, public_id=public.id)
        return redirect(url_for("publics.show_public", tag=tag))
    
    return render_template("posts/create.html", public=public)


@posts_bp.route("/post/edit/<int:post_id>", methods=["GET","POST"])
def edit_post(post_id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    user = get_user_by_id(session.get("user_id"))
    post = get_post(post_id, user)
    if post is None:
        abort(404)

    if not can_edit_post(user, post):
        abort(403)

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

    if not can_delete_post(user, post):
        abort(403)

    if post is None:
        abort(404)
    delete_post(post_id)
    return redirect(url_for("posts.feed"))
