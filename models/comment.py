from datetime import datetime, UTC
from database.db import db
from utils.permissions import can_view_content

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    is_hidden = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    
    author = db.relationship('User', backref=db.backref('user_comments', lazy='dynamic'))
    post = db.relationship('Post', backref=db.backref('post_comments', lazy='dynamic'))
    likes = db.relationship('CommentLike', back_populates='comment', lazy='dynamic')


def get_comments_for_post(post, user=None, sort=1):
    sort = int(sort) if sort else 1
    comments = db.session.query(Comment).filter_by(post_id=post.id).all()
    comments = [comment for comment in comments if can_view_content(user, post, comment)]
    if sort == 1:
        comments.sort(key=lambda c: c.created_at, reverse=True)
    else:
        comments.sort(key=lambda c: c.likes.count(), reverse=True)

    return comments

def get_comment(comment_id):
    comment = db.session.get(Comment, comment_id)
    return comment

def add_comment(post_id, user_id, content):
    comment = Comment(author_id=user_id, post_id=post_id, content=content)
    
    db.session.add(comment)
    db.session.commit()

def update_comment(comment_id, content):
    comment = db.session.get(Comment, comment_id)
    
    if comment:
        comment.content = content
        db.session.commit()
        return True
    
    return False

def delete_comment(comment_id):
    comment = db.session.get(Comment, comment_id)
        
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return True

    return False

def toggle_hide_comment(comment_id):
    comment = db.session.get(Comment, comment_id)
        
    if comment:
        comment.is_hidden = 0 if comment.is_hidden else 1
        db.session.commit()
        return True

    return False