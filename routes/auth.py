from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User, register_user, login_user
from utils.validators import is_valid_tag, is_valid_username, is_valid_password
from utils.helpers import generate_unique_tag

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        tag = request.form.get("tag", "").strip().lower()
        password = request.form.get("password", "").strip()
        
        if not is_valid_username(username):
            return render_template("auth/register.html", 
                                error="Username must be 2-20 characters",
                                username=username, tag=tag)
        
        if not is_valid_password(password):
            return render_template("auth/register.html", 
                                error="Password must be 6-128 characters with uppercase and digit",
                                username=username, tag=tag)
        
        if not tag:
            tag = generate_unique_tag(username)
            return render_template("auth/register.html",
                                info="Tag generated automatically. Confirm to register.",
                                username=username, tag=tag)
        
        if not is_valid_tag(tag):
            return render_template("auth/register.html",
                                error="Tag must be 3-20 chars, only a-z, 0-9, _",
                                username=username, tag=tag)
        
        if User.query.filter_by(tag=tag).first():
            return render_template("auth/register.html",
                                error="Tag already taken",
                                username=username, tag=tag)
        
        user = register_user(username=username, tag=tag, password=password)
        
        session["user_id"] = user.id
        session["tag"] = user.tag
        session["role"] = user.role
        session["avatar"] = user["avatar"]
        return redirect(url_for("posts.feed"))
    
    return render_template("auth/register.html", error=None)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        tag = request.form.get("tag", "").strip()
        password = request.form.get("password", "").strip()
        
        user = login_user(tag, password)

        if user:
            if user.is_banned:
                return render_template("auth/login.html", error="User is banned", tag=tag)
            session["user_id"] = user.id
            session["tag"] = user.tag
            session["role"] = user.role
            session["avatar"] = user.avatar
            return redirect(url_for("posts.feed"))
        
        return render_template("auth/login.html", error="Incorrect tag or password", tag=tag)
    
    return render_template("auth/login.html")
