from datetime import datetime, UTC
from database.db import db
from utils.permissions import can_view_content
from models.comment import Comment

class Reply(db.Model):
    __tablename__ = "replies"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    parent_reply_id = db.Column(db.Integer, db.ForeignKey('replies.id'))
    content = db.Column(db.String(500), nullable=False)
    is_hidden = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    
    author = db.relationship('User', backref=db.backref('user_replies', lazy='dynamic'))
    post = db.relationship('Post', backref=db.backref('post_replies', lazy='dynamic'))
    comment = db.relationship('Comment', backref=db.backref('comment_replies', lazy='dynamic'))
    parent_reply = db.relationship('Reply', backref=db.backref('parent_replies', lazy='dynamic'), remote_side=[id])
    likes = db.relationship('ReplyLike', back_populates='reply', lazy='dynamic')


def get_replies_for_post(post, user=None):
    replies = db.session.query(Reply).filter_by(post_id=post.id).all()
    replies = [reply for reply in replies if can_view_content(user, post, reply)]
    replies.sort(key=lambda c: c.created_at, reverse=True)

    return replies

def get_reply(reply_id):
    reply = db.session.query(Reply).filter_by(id=reply_id).first()
    return reply

def add_reply(comment_id, user_id, content):
    comment = db.session.get(Comment, comment_id)
    reply = Reply(author_id=user_id, post_id=comment.post_id, comment_id=comment_id, content=content)
    
    db.session.add(reply)
    db.session.commit()

def add_reply_to_reply(comment_id, parent_reply_id, user_id, content):
    comment = db.session.get(Comment, comment_id)
    reply = Reply(author_id=user_id, post_id=comment.post_id, comment_id=comment_id, parent_reply_id=parent_reply_id, content=content)
    
    db.session.add(reply)
    db.session.commit()

def update_reply(reply_id, content):
    reply = db.session.get(Reply, reply_id)
    
    if reply:
        reply.content = content
        db.session.commit()
        return True
    
    return False

def delete_reply(reply_id):
    reply = db.session.get(Reply, reply_id)
        
    if reply:
        db.session.delete(reply)
        db.session.commit()
        return True

    return False

def hide_reply(reply_id):
    reply = db.session.get(Reply, reply_id)
        
    if reply:
        reply.is_hidden = 0 if reply.is_hidden else 1
        db.session.commit()
        return True

    return False