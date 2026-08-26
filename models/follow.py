from datetime import datetime, UTC
from database.db import db
from models.public import Public, PublicMember

class Follow(db.Model):
    __tablename__ = "follows"

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    
    follower = db.relationship('User', foreign_keys=[follower_id], backref=db.backref('following', lazy='dynamic'))
    following = db.relationship('User', foreign_keys=[following_id], backref=db.backref('followers', lazy='dynamic'))
    
    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id', name='unique_'),)

#Функции: follow_user, unfollow_user, is_following, get_followers, get_following

def follow_user(follower_id, following_id):
    if follower_id != following_id:
        follow = Follow(follower_id=follower_id, following_id=following_id)
        db.session.add(follow)
        db.session.commit()

def unfollow_user(follower_id, following_id):
    follow = db.session.query(Follow).filter_by(follower_id=follower_id, following_id=following_id).first()
    if follow:
        db.session.delete(follow)
        db.session.commit()

def is_following(follower_id, following_id):
    follow = db.session.query(Follow).filter_by(follower_id=follower_id, following_id=following_id).first()
    return follow is not None

def get_following(follower_id):
    return db.session.query(Follow).filter_by(follower_id=follower_id).all()

def get_followers(following_id):
    return db.session.query(Follow).filter_by(following_id=following_id).all()



def follow_public(public_id, member_id):
    member = PublicMember(public_id=public_id, user_id=member_id, role="member")
    db.session.add(member)
    db.session.commit()

def unfollow_public(public_id, member_id):
    member = db.session.query(PublicMember).filter_by(public_id=public_id, user_id=member_id).first()
    if member:
        db.session.delete(member)
        db.session.commit()

def is_following_public(public_id, member_id):
    member = db.session.query(PublicMember).filter_by(public_id=public_id, user_id=member_id).first()
    return member is not None