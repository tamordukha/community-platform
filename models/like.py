from datetime import datetime, UTC
from database.db import db

class PostLike(db.Model):
    __tablename__ = "post_likes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    user = db.relationship('User', backref=db.backref('post_likes', lazy='dynamic'))
    post = db.relationship('Post', back_populates='likes')

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_post_like'),)

class CommentLike(db.Model):
    __tablename__ = "comment_likes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    user = db.relationship('User', backref=db.backref('comment_likes', lazy='dynamic'))
    comment = db.relationship('Comment', back_populates='likes')

    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='unique_comment_like'),)

class ReplyLike(db.Model):
    __tablename__ = "reply_likes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reply_id = db.Column(db.Integer, db.ForeignKey('replies.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    user = db.relationship('User', backref=db.backref('reply_likes', lazy='dynamic'))
    reply = db.relationship('Reply', back_populates='likes')

    __table_args__ = (db.UniqueConstraint('user_id', 'reply_id', name='unique_reply_like'),)


def toggle_like_post(user_id, post_id):
    post_like = db.session.query(PostLike).filter_by(post_id=post_id, user_id=user_id).first()
    if post_like:
        db.session.delete(post_like)
    else:
        post_like = PostLike(user_id=user_id, post_id=post_id)
        db.session.add(post_like)
    db.session.commit()

def toggle_like_comment(user_id, comment_id):
    comment_like = db.session.query(CommentLike).filter_by(comment_id=comment_id, user_id=user_id).first()
    if comment_like:
        db.session.delete(comment_like)
    else:
        comment_like = CommentLike(user_id=user_id, comment_id=comment_id)
        db.session.add(comment_like)
    db.session.commit()

def toggle_like_reply(user_id, reply_id):
    reply_like = db.session.query(ReplyLike).filter_by(reply_id=reply_id, user_id=user_id).first()
    if reply_like:
        db.session.delete(reply_like)
    else:
        reply_like = ReplyLike(user_id=user_id, reply_id=reply_id)
        db.session.add(reply_like)
    db.session.commit()

def get_post_like(user_id, post_id):
    return db.session.query(PostLike).filter_by(user_id=user_id, post_id=post_id).first()

def get_comment_like(user_id, comment_id):
    return db.session.query(CommentLike).filter_by(user_id=user_id, comment_id=comment_id).first()

def get_reply_like(user_id, reply_id):
    return db.session.query(ReplyLike).filter_by(user_id=user_id, reply_id=reply_id).first()

def get_post_likes_count(post_id):
    return db.session.query(PostLike).filter_by(post_id=post_id).count()

def get_comment_likes_count(comment_id):
    return db.session.query(CommentLike).filter_by(comment_id=comment_id).count()

def get_reply_likes_count(reply_id):
    return db.session.query(ReplyLike).filter_by(reply_id=reply_id).count()