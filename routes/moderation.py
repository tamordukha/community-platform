from flask import Flask, Blueprint, current_app, render_template, request, redirect, url_for, session, abort, flash, jsonify
from models.ban import get_filter_bans
from models.user import get_user_by_id

moderation_bp = Blueprint("moderation", __name__)

@moderation_bp.route("/moderation", methods=["GET","POST"])
def moderation_page():
    return redirect(url_for("posts.feed"))