from datetime import datetime, timedelta, UTC
from database.db import db

class Mute(db.Model):
    __tablename__ = "mutes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    moderator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    expires_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('mutes_received', lazy='dynamic'))
    moderator = db.relationship('User', foreign_keys=[moderator_id], backref=db.backref('mutes_given', lazy='dynamic'))


def mute_user(user_id, moderator_id, reason, expires_at):
    if is_muted(user_id):
        return None

    mute = Mute(
        user_id      = user_id,
        moderator_id = moderator_id ,
        reason       = reason,
        is_active    = True,
        expires_at   = expires_at
    )

    db.session.add(mute)
    db.session.commit()


def unmute_user(mute_id):
    mute = db.session.get(Mute, mute_id)
    if mute:
        mute.is_active = False
        db.session.commit()


def is_muted(user_id):
    mute = db.session.query(Mute).filter_by(user_id=user_id, is_active=True).first()
    if not mute:
        return False
    return mute.expires_at > datetime.now(UTC)


def get_mute(mute_id):
    return db.session.get(Mute, mute_id)


def get_filter_mutes(user_id=None, moderator_id=None, is_active=None):
    query = db.session.query(Mute)

    if user_id is not None:
        query = query.filter_by(user_id=user_id)

    if moderator_id is not None:
        query = query.filter_by(moderator_id=moderator_id)

    if is_active is not None:
        query = query.filter_by(is_active=is_active)

    return query.all()