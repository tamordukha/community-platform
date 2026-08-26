from flask import Flask, Blueprint, current_app, render_template, request, redirect, url_for, session, flash, abort, jsonify, send_from_directory
import os
from models.public import (get_public_by_id, get_public_by_tag,
                           add_public, update_public, delete_public,
                           update_public_avatar, update_public_banner,
                           get_member, get_member_by_id,
                           get_public_members, update_member_role,
                           is_member, follow_public, unfollow_public)
from models.user import get_user_by_id
from models.post import get_posts
from utils.permissions import can_edit_public, can_delete_public, can_change_member_role, can_kick_member
from utils.validators import is_valid_username, is_valid_tag, is_valid_bio, validate_image
from utils.helpers import generate_unique_tag
#from config import Config

publics_bp = Blueprint('publics', __name__)

#show_public, create_public, edit_public, delete_public, 

@publics_bp.route("/public/<tag>")
def show_public(tag):
    if session.get("user_id"):
        current_user = get_user_by_id(session.get("user_id"))
    else:
        current_user = None
    
    public = get_public_by_tag(tag)
    
    if public is None:
        abort(404)
    
    posts = get_posts(user=current_user, public=public)

    return render_template(
        "publics/view_public.html", 
        current_user=current_user, 
        public=public, 
        posts=posts,
        show_bottom_bar=True
    )

@publics_bp.route("/publics/create", methods=["GET","POST"])
def create_public():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    
    user = get_user_by_id(session.get("user_id"))

    if request.method == "POST":
        name = request.form.get("name")
        tag = request.form.get("tag")
        bio = request.form.get("bio")
        avatar = request.files["avatar"] if "avatar" in request.files else None
        banner = request.files["banner"] if "banner" in request.files else None
        
        if not is_valid_username(name):
            return render_template("publics/create.html", 
                            error="Name must be 2-20 characters",
                            name=name, tag=tag, bio=bio)

        if not tag:
            tag = generate_unique_tag(name)
            return render_template("publics/create.html",
                            info="Tag generated automatically. Confirm to register.",
                            name=name, tag=tag, bio=bio)
        
        if not is_valid_tag(tag):
            return render_template("publics/create.html",
                            error="Tag must be 3-20 chars, only a-z, 0-9, _",
                            name=name, tag=tag, bio=bio)

        if bio and not is_valid_bio(bio):
            return render_template("publics/create.html",
                            error="Bio must be max 150 chars",
                            name=name, tag=tag, bio=bio)

        if avatar and avatar.filename != "":
            if not validate_image(avatar):
                flash("Invalid image", "error")
                return render_template("publics/create.html",
                                error="Invalid image format",
                                name=name, tag=tag, bio=bio, avatar=avatar, banner=banner)

        if banner and banner.filename != "":
            if not validate_image(banner):
                flash("Invalid image", "error")
                return render_template("publics/create.html",
                                error="Invalid image format",
                                username=name, tag=tag, bio=bio, avatar=avatar, banner=banner)

        public = add_public(user.id, name, tag, bio=bio)
        if public is None:
            return render_template("publics/create.html", error="Tag already taken", name=name, tag=tag, bio=bio)

        if avatar and avatar.filename != "":
            avatar_ext = avatar.filename.rsplit('.', 1)[1].lower()
            avatar_filename = f"{public.id}.{avatar_ext}"
            update_public_avatar(public.id, avatar, avatar_filename)

        if banner and banner.filename != "":
            banner_ext = banner.filename.rsplit('.', 1)[1].lower()
            banner_filename = f"{public.id}.{banner_ext}"
            update_public_banner(public.id, banner, banner_filename)

        return redirect(url_for("publics.show_public", tag=tag))
    
    return render_template("publics/create.html")


@publics_bp.route("/publics/edit/<tag>", methods=["GET","POST"])
def edit_public(tag):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    
    user = get_user_by_id(session.get("user_id"))
    public = get_public_by_tag(tag)

    if not user:
        return abort(401)
    
    if not public:
        return abort(404)
    
    member = get_member(user.id, public.id)

    if not member:
        return abort(404)
    
    if not can_edit_public(member, public):
        return abort(404)

    if request.method == "POST":
        name = request.form.get("name") if "name" in request.form else public.name
        tag = request.form.get("tag") if "tag" in request.form else public.tag
        bio = request.form.get("bio") if "bio" in request.form else public.bio
        avatar = request.files["avatar"] if "avatar" in request.files else None
        banner = request.files["banner"] if "banner" in request.files else None
        
        if not is_valid_username(name):
            return render_template("publics/edit.html", 
                            error="Name must be 2-20 characters",
                            name=name, tag=tag, bio=bio, current_avatar=public.avatar, current_banner=public.banner)
        
        if not is_valid_tag(tag):
            return render_template("publics/edit.html",
                            error="Tag must be 3-20 chars, only a-z, 0-9, _",
                            name=name, tag=tag, bio=bio, current_avatar=public.avatar, current_banner=public.banner)

        if bio and not is_valid_bio(bio):
            return render_template("publics/edit.html",
                            error="Bio must be max 150 chars",
                            name=name, tag=tag, bio=bio, current_avatar=public.avatar, current_banner=public.banner)

        if avatar and avatar.filename != "":
            if not validate_image(avatar):
                flash("Invalid image", "error")
                return render_template("publics/edit.html",
                                error="Invalid image format",
                                name=name, tag=tag, bio=bio, current_avatar=public.avatar, current_banner=public.banner)

        if banner and banner.filename != "":
            if not validate_image(banner):
                flash("Invalid image", "error")
                return render_template("publics/edit.html",
                                error="Invalid image format",
                                name=name, tag=tag, bio=bio, current_avatar=public.avatar, current_banner=public.banner)

        updated = update_public(public.id, name, tag, bio=bio)
        if not updated:
            return render_template("publics/edit.html", error="Tag already taken", name=name, tag=tag, bio=bio)

        if avatar and avatar.filename != "":
            avatar_ext = avatar.filename.rsplit('.', 1)[1].lower()
            avatar_filename = f"{public.id}.{avatar_ext}"
            update_public_avatar(public.id, avatar, avatar_filename)

        if banner and banner.filename != "":
            banner_ext = banner.filename.rsplit('.', 1)[1].lower()
            banner_filename = f"{public.id}.{banner_ext}"
            update_public_banner(public.id, banner, banner_filename)

        return redirect(url_for("publics.show_public", tag=tag))
    
    return render_template("publics/edit.html", public=public, user=user)


@publics_bp.route("/publics/delete/<tag>", methods=["POST"])
def del_public(tag):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    
    public = get_public_by_tag(tag)

    if not public:
        return abort(404)
    
    member = get_member(user_id, public.id)

    if not member:
        return abort(404)
    
    if not can_delete_public(member, public):
        return abort(404)

    deleted = delete_public(public.id)
    if not deleted:
        return redirect(url_for("publics.show_public", tag=tag))
    
    return redirect(url_for("posts.index"))


@publics_bp.route("/avatar/<int:public_id>", methods=["POST"])
def update_avatar(public_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    public = get_public_by_id(public_id)

    if not public:
        return abort(404)

    member = get_member(user_id, public_id)

    if not member:
        return abort(404)

    if not can_edit_public(member, public):
        return abort(404)

    if "avatar" not in request.files:
        return redirect(url_for("publics.show_public", tag=public.tag))

    file = request.files["avatar"]

    if file.filename == "":
        return redirect(url_for("publics.show_public", tag=public.tag))
    if not validate_image(file):
        flash("Invalid image", "error")
        return redirect(url_for("publics.show_public", tag=public.tag))

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{public_id}.{ext}"
    update_public_avatar(public_id, file, filename)
    
    return redirect(url_for("publics.show_public", tag=public.tag))


@publics_bp.route("/banner/<int:public_id>", methods=["POST"])
def update_banner(public_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    public = get_public_by_id(public_id)

    if not public:
        return abort(404)

    member = get_member(user_id, public_id)

    if not member:
        return abort(404)

    if not can_edit_public(member, public):
        return abort(404)

    if "banner" not in request.files:
        return redirect(url_for("publics.show_public", tag=public.tag))

    file = request.files["banner"]

    if file.filename == "":
        return redirect(url_for("publics.show_public", tag=public.tag))
    if not validate_image(file):
        flash("Invalid image", "error")
        return redirect(url_for("publics.show_public", tag=public.tag))

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{public_id}.{ext}"
    update_public_banner(public_id, file, filename)
    
    return redirect(url_for("publics.show_public", tag=public.tag))


@publics_bp.route("/publics/followers/<tag>")
def show_public_followers(tag):
    public = get_public_by_tag(tag)

    if not public: 
        return abort(404)

    members = get_public_members(public.id)

    return render_template("publics/followers.html", public=public, members=members)


@publics_bp.route("/publics/follow/<int:public_id>", methods=["POST"])
def toggle_follow(public_id):
    user_id = session.get("user_id")
    if not user_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))
    
    public = get_public_by_id(public_id)

    if public is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Public not found"}), 404
        return abort(404)

    if is_member(user_id, public_id):
        unfollow_public(user_id, public_id)
        following = False
    else:
        follow_public(user_id, public_id)
        following = True

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"following": following})
    
    return redirect(url_for("publics.show_public", tag=public.tag))


@publics_bp.route("/publics/<tag>/members/<int:member_id>/role", methods=["POST"])
def change_role(tag, member_id):
    user_id = session.get("user_id")
    if not user_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("publics.show_public_followers", tag=tag))

    public = get_public_by_tag(tag)
    if not public:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Public not found"}), 404
        return abort(404)

    current_member = get_member(user_id, public.id)
    member = get_member_by_id(member_id)
    if not member or not current_member:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Member not found"}), 404
        return abort(404)

    new_role = request.form.get("new_role")

    if can_change_member_role(current_member, member, new_role):
        update_member_role(member, new_role)
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant change role"}), 403
        return abort(403)
        
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"new_role": new_role})
    
    return redirect(url_for("publics.show_public_followers", tag=tag))


@publics_bp.route("/publics/<tag>/members/<int:member_id>/kick", methods=["POST"])
def kick_member(tag, member_id):
    user_id = session.get("user_id")
    if not user_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("publics.show_public_followers", tag=tag))

    public = get_public_by_tag(tag)
    if not public:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Public not found"}), 404
        return abort(404)

    current_member = get_member(user_id, public.id)
    member = get_member_by_id(member_id)
    if not member or not current_member:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Member not found"}), 404
        return abort(404)

    if can_kick_member(current_member, member):
        kicked = True
        unfollow_public(member.user_id, public.id)
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant change role"}), 403
        return abort(403)
        
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"kicked": kicked})
    
    return redirect(url_for("publics.show_public_followers", tag=tag))