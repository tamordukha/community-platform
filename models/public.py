from flask import current_app
import os
from datetime import datetime, UTC
from database.db import db
from models.user import get_user_by_tag

class Public(db.Model):
    __tablename__ = "publics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    tag = db.Column(db.String(50), unique=True, nullable=False)
    is_banned = db.Column(db.Boolean, default=False, nullable=False)
    avatar = db.Column(db.String(255))
    banner = db.Column(db.String(255))
    bio = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

class PublicMember(db.Model):
    __tablename__ = "public_members"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    public_id = db.Column(db.Integer, db.ForeignKey('publics.id'), nullable=False)
    role = db.Column(db.String(20), default="member", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    user = db.relationship('User', backref=db.backref('public_members', lazy='dynamic'))
    public = db.relationship('Public', backref=db.backref('members', lazy='dynamic'))

    __table_args__ = (db.UniqueConstraint('user_id', 'public_id', name='unique_public_member'),)


def get_public_by_id(id):
    public = db.session.query(Public).filter_by(id=id).first()
    return public

def get_public_by_tag(tag):
    public = db.session.query(Public).filter_by(tag=tag).first()
    return public

def get_public_members(public_id):
    members = db.session.query(PublicMember).filter_by(public_id=public_id).all()
    return members

def add_public(owner_id ,name, tag, avatar=None, banner=None, bio=None):
    if get_user_by_tag(tag) or get_public_by_tag(tag):
        return None

    public = Public(name=name, tag=tag)
    public.avatar = avatar if avatar else None
    public.banner = banner if banner else None
    public.bio = bio if bio else None

    owner = PublicMember(user_id=owner_id, public_id=public.id, role="owner")

    db.session.add(public)
    db.session.add(owner)
    db.session.commit()

    return public

def update_public(public_id, name, tag, avatar=None, banner=None, bio=None):
    if get_user_by_tag(tag) or get_public_by_tag(tag):
        return False
    existing = get_public_by_tag(tag)
    if existing and existing.id != public_id:
        return False

    public = db.session.get(Public, public_id)

    if public:
        public.name = name
        public.tag = tag
        public.avatar = avatar if avatar else None
        public.banner = banner if banner else None
        public.bio = bio if bio else None
        db.session.commit()
        return True
    
    return False

def delete_public(public_id):
    public = db.session.get(Public, public_id)

    if public:
        PublicMember.query.filter_by(public_id=public_id).delete()
        db.session.delete(public)
        db.session.commit()
        return True
    
    return False

def update_public_avatar(public_id, file, filename):
    file.save(os.path.join(current_app.config["AVATAR_FOLDER"], filename))
    
    public = db.session.get(Public, public_id)
    if public:
        public.avatar = filename
        db.session.commit()

def update_public_banner(public_id, file, filename):
    file.save(os.path.join(current_app.config["BANNER_FOLDER"], filename))
    
    public = db.session.get(Public, public_id)
    if public:
        public.banner = filename
        db.session.commit()

    
def get_member(user_id, public_id):
    return db.session.query(PublicMember).filter_by(user_id=user_id, public_id=public_id).first()

def get_member_by_id(id):
    member = db.session.query(PublicMember).filter_by(id=id).first()
    return member

def get_member_by_user_id(user_id):
    member = db.session.query(PublicMember).filter_by(user_id=user_id).all()
    return member

def get_member_publics(user_id):
    publics = (db.session.query(Public)
                .join(PublicMember)
                .filter(PublicMember.user_id == user_id)
                .all())
    return publics

def is_member(user_id, public_id):
    member = db.session.query(PublicMember).filter_by(user_id=user_id, public_id=public_id).first()

def follow_public(user_id, public_id):
    member = PublicMember(user_id=user_id, public_id=public_id, role="member")
    db.session.add(member)
    db.session.commit()

def unfollow_public(user_id, public_id):
    member = db.session.query(PublicMember).filter_by(user_id=user_id, public_id=public_id).first()
    if member:
        db.session.delete(member)
        db.session.commit()

def update_member_role(member, role):
    member.role = role
    db.session.commit()

def toggle_ban_public(public_id):
    public = db.session.get(Public, public_id)
    if public:
        public.is_banned = not public.is_banned
        db.session.commit()