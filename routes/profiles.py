from flask import Flask, Blueprint, current_app, render_template, request, redirect, url_for, session, abort, flash, jsonify
from models.user import get_user_by_id, update_user_avatar, update_user_role
from models.post import get_posts
from utils.permissions import can_modify_role, can_change_role
from utils.validators import validate_image


profiles_bp = Blueprint('profiles', __name__)

@profiles_bp.route("/profiles/<int:profile_user_id>")
def profile(profile_user_id):
    if session.get("user_id"):
        current_user = get_user_by_id(session.get("user_id"))
    else:
        current_user = None
    
    profile_user = get_user_by_id(profile_user_id)
    
    if profile_user is None:
        abort(404)
    
    posts = get_posts(user=current_user, profile_user=profile_user)

    return render_template(
        "profile/profile.html", 
        current_user=current_user, 
        profile_user=profile_user, 
        posts=posts,
        can_modify_role=can_modify_role,
        can_change_role=can_change_role,
        show_bottom_bar=True
    )

@profiles_bp.route("/avatar/<int:profile_user_id>", methods=["POST"])
def update_avatar(profile_user_id):
    user_id = session.get("user_id")
    if not user_id or user_id != profile_user_id:
        return redirect(url_for("profiles.profile", profile_user_id=profile_user_id))

    if "avatar" not in request.files:
        return redirect(url_for("profiles.profile", profile_user_id=profile_user_id))

    file = request.files["avatar"]

    if file.filename == "":
        return redirect(url_for("profiles.profile", profile_user_id=profile_user_id))
    if not validate_image(file):
        flash("Invalid image", "error")
        return redirect(url_for("profiles.profile", profile_user_id=profile_user_id))

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{user_id}.{ext}"
    update_user_avatar(user_id, file, filename)

    session['avatar'] = filename
    
    return redirect(url_for("profiles.profile", profile_user_id=profile_user_id))



@profiles_bp.route("/role/<int:profile_user_id>", methods=["POST"])
def change_role(profile_user_id):
    if not session.get("user_id") or session.get("role")=="user":
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("profile.profile", profile_user_id=profile_user_id))
    
    current_user=get_user_by_id(session["user_id"])
    profile_user = get_user_by_id(profile_user_id)
    new_role = request.form.get("new_role")

    if profile_user is None:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "User not found"}), 404
        abort(404)

    if can_change_role(current_user, profile_user, new_role):
        update_user_role(profile_user, new_role)
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "You cant change role"}), 403
        abort(403)
        
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"new_role": new_role})
    
    return redirect(url_for("profile.profile", profile_user_id=profile_user_id))