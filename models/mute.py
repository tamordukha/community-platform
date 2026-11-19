from datetime import datetime, timedelta, UTC
from database.db import db

class Mute(db.Model):
    __tablename__ = "mutes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    muted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    expires_at = db.Column(db.DateTime, nullable=False)
    unmuted_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    unmuted_at = db.Column(db.DateTime)

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('mutes_received', lazy='dynamic'))
    muted_by = db.relationship('User', foreign_keys=[muted_by_id], backref=db.backref('mutes_given', lazy='dynamic'))
    unmuted_by = db.relationship('User', foreign_keys=[unmuted_by_id])


def mute_user(user_id, moderator_id, reason, expires_at=None):
    if is_muted(user_id):
        return None
    
    if expires_at is None:
        expires_at = datetime.now(UTC) + timedelta(hours=24)

    mute = Mute(
        user_id      = user_id,
        muted_by_id = moderator_id ,
        reason       = reason,
        expires_at   = expires_at,
    )

    db.session.add(mute)
    db.session.commit()


def unmute_user(mute_id, moderator_id):
    mute = db.session.get(Mute, mute_id)
    if mute and mute.is_active:
        mute.is_active = False
        mute.unmuted_by_id = moderator_id
        mute.unmuted_at = datetime.now(UTC)
        db.session.commit()


def is_muted(user_id):
    mute = db.session.query(Mute).filter_by(user_id=user_id).first()
    if not mute:
        return False

    expires = mute.expires_at.replace(tzinfo=UTC)
    return expires > datetime.now(UTC)


def get_mute(mute_id):
    return db.session.get(Mute, mute_id)


def get_filter_mutes(
    user_id=None, is_active=None,
    muted_by_id=None, unmuted_by_id=None,
    ascending=False, limit=50, offset=0
    ):
    query = db.session.query(Mute)

    if user_id:
        query = query.filter_by(user_id=user_id)

    if muted_by_id:
        query = query.filter_by(muted_by_id=muted_by_id)

    if unmuted_by_id:
        query = query.filter_by(unmuted_by_id=unmuted_by_id)

    if is_active is not None:
        query = query.filter_by(is_active=is_active)

    mutes = query.offset(offset).limit(limit).all()

    if ascending:
        return mutes.reverse()

    return mutes


def expire_mutes():
    now = datetime.now(UTC).replace(tzinfo=None)

    db.session.query(Mute).filter(
        Mute.is_active == True,
        Mute.expires_at < now
    ).update({"is_active": False})

    db.session.commit()