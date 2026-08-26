from datetime import datetime, UTC
from database.db import db
from utils.permissions import can_view_post
from services.feed_service import calculate_post_score

class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    public_id = db.Column(db.Integer, db.ForeignKey('publics.id'))
    content = db.Column(db.Text, nullable=False)
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    
    author = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))
    public = db.relationship('Public', backref=db.backref('public_posts', lazy='dynamic'))
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')


def get_posts(user=None, profile_user=None, public=None, feed=False):
    query = db.session.query(Post).order_by(Post.created_at.desc())
    
    if profile_user:
        query = query.filter_by(author_id=profile_user.id)

    if public:
        query = query.filter_by(public_id=public.id)

    posts = [post for post in query.all() if can_view_post(user, post)]
    
    if feed:
        posts_with_score = [(post, calculate_post_score(post)) for post in posts]
        posts_with_score.sort(key=lambda x: x[1], reverse=True)
        posts = [post for post, score in posts_with_score]
    
    return posts

def get_post(post_id, user=None):
    post = db.session.query(Post).filter_by(id=post_id).first()
    return post if can_view_post(post, user) else None

def add_post(content, is_public, user_id=None, public_id=None):
    if (user_id is None and public_id is None) or (user_id is not None and public_id is not None):
        return None
    
    post = Post(
        author_id=user_id,
        public_id=public_id,
        content=content,
        is_public=is_public
    )
    db.session.add(post)
    db.session.commit()
    return post

def update_post(post_id, content, is_public):
    post = db.session.get(Post, post_id)
    
    if post:
        post.content = content
        post.is_public = is_public
        db.session.commit()
        return True
    
    return False

def delete_post(post_id):
    post = db.session.query(Post).get(post_id)
        
    if post:
        db.session.delete(post)
        db.session.commit()
        return True

    return False