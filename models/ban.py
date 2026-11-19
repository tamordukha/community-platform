from datetime import datetime, UTC
from database.db import db

class Ban(db.Model):
    __tablename__ = "bans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    banned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    unbanned_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    unbanned_at = db.Column(db.DateTime)

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('bans_received', lazy='dynamic'))
    banned_by = db.relationship('User', foreign_keys=[banned_by_id], backref=db.backref('bans_given', lazy='dynamic'))
    unbanned_by = db.relationship('User', foreign_keys=[unbanned_by_id])


def ban_user(user_id, moderator_id, reason):
    if is_banned(user_id):
        return None

    ban = Ban(
        user_id=user_id,
        banned_by_id=moderator_id,
        reason=reason
    )

    db.session.add(ban)
    db.session.commit()


def unban_user(ban_id, moderator_id):
    ban = db.session.get(Ban, ban_id)
    if ban and ban.is_active:
        ban.is_active = False
        ban.unbanned_by_id = moderator_id
        ban.unbanned_at = datetime.now(UTC)
        db.session.commit()


def is_banned(user_id):
    ban = db.session.query(Ban).filter_by(user_id=user_id, is_active=True).first()
    return ban is not None


def get_ban(ban_id):
    return db.session.get(Ban, ban_id)


def get_filter_bans(
    user_id=None, is_active=None,
    banned_by_id=None, unbanned_by_id=None,
    ascending=False, limit=50, offset=0
    ):
    query = db.session.query(Ban)

    if user_id:
        query = query.filter_by(user_id=user_id)

    if banned_by_id:
        query = query.filter_by(banned_by_id=banned_by_id)
    
    if unbanned_by_id:
        query = query.filter_by(unbanned_by_id=unbanned_by_id)

    if is_active is not None:
        query = query.filter_by(is_active=is_active)

    bans = query.offset(offset).limit(limit).all()

    if ascending:
        return bans.reverse()

    return bans

    