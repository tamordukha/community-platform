from flask import Flask, Blueprint, current_app, render_template, request, redirect, url_for, session, abort, flash, jsonify
from models.ban import get_filter_bans
from models.user import get_user_by_id

from utils.permissions import can_modify_role

bans_bp = Blueprint("bans", __name__)

'''
@bans_bp.route("/moderation", methods=["GET","POST"])
def moderation_page()
'''