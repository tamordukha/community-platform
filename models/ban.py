from datetime import datetime, UTC
from database.db import db

from models.user import User

class Ban(db.Model):
    __tablename__ = "bans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    moderator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))


def ban_user(user_id, moderator_id, reason):
    if is_banned(user_id):
        return None

    ban = Ban(
        user_id      = user_id,
        moderator_id = moderator_id ,
        reason       = reason,
        is_active    = True
    )

    db.session.add(ban)
    db.session.commit()


def unban_user(ban_id):
    ban = db.session.get(Ban, ban_id)
    if ban:
        ban.is_active = False
        db.session.commit()


def is_banned(user_id):
    ban = db.session.query(Ban).filter_by(user_id=user_id, is_active=True).first()
    return ban is not None


def get_ban(ban_id):
    return db.session.get(Ban, ban_id)


def get_filter_bans(user_id=None, moderator_id=None, is_active=None):
    query = db.session.query(Ban)

    if user_id is not None:
        query = query.filter_by(user_id=user_id)

    if moderator_id is not None:
        query = query.filter_by(moderator_id=moderator_id)

    if is_active is not None:
        query = query.filter_by(is_active=is_active)

    return query.all()