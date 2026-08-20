from datetime import datetime, UTC
from database.db import db
from models.post import Post

class Repost(db.Model):
    __tablename__ = "reposts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    user = db.relationship('User', backref=db.backref('reposts', lazy='dynamic'))
    post = db.relationship('Post', backref=db.backref('reposts', lazy='dynamic'))

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_repost'),)

def get_reposts_for_user(user_id):
    reposts = db.session.query(Repost).filter_by(user_id=user_id).all()
    return reposts

def toggle_repost(user_id, post_id):
    repost = db.session.query(Repost).filter_by(user_id=user_id, post_id=post_id).first()
    if repost:
        db.session.delete(repost)
    else:
        repost = Repost(user_id=user_id, post_id=post_id)
        db.session.add(repost)
    db.session.commit()

def is_repost(user_id, post_id):
    repost = db.session.query(Repost).filter_by(user_id=user_id, post_id=post_id).first()
    return repost is not None

def get_repost_count_for_post(post_id):
    count = db.session.query(Repost).filter_by(post_id=post_id).count()
    return count