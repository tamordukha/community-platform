from datetime import datetime, UTC
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    tag = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)
    avatar = db.Column(db.String(255))
    banner = db.Column(db.String(255))
    bio = db.Column(db.String(150))
    city = db.Column(db.String(50))
    birthdate = db.Column(db.String(10))
    profile_track_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))


def register_user(username, tag, password):
    user = db.session.query(User).filter_by(tag=tag).first()
    if user is not None:
        return None
    hashed_password = generate_password_hash(password)
    user = User(username=username, tag=tag, password=hashed_password)

    db.session.add(user)
    db.session.commit()

    return user

def login_user(tag, password):
    user = db.session.query(User).filter_by(tag=tag).first()
    if user is None:
        return None

    if check_password_hash(user.password, password):
        return user

    return None