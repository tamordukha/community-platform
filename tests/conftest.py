import pytest
import os
import tempfile
from app import create_app
from database.db import db, init_db

from models import *
from models.user import update_user_role

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })
    
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    
    with app.app_context():
        db.create_all()
    
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)



@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(app):
    client = app.test_client()
    client.post("/register", data={
        "username": "Username",
        "tag": "user_tag",
        "password": "user_password",
    })
    client.post("/login", data={
        "tag": "user_tag",
        "password": "user_password",
    })
    return client


@pytest.fixture
def auth_foreign_client(app):
    client = app.test_client()
    client.post("/register", data={
        "username": "Username2",
        "tag": "user_tag2",
        "password": "user_password2",
    })
    client.post("/login", data={
        "tag": "user_tag2",
        "password": "user_password2",
    })
    return client


@pytest.fixture
def auth_mod_client(app):
    client = app.test_client()
    client.post("/register", data={
        "username": "Moder_username",
        "tag": "moder_tag",
        "password": "moder_password",
    })
    client.post("/login", data={
        "tag": "moder_tag",
        "password": "moder_password",
    })
    
    # Меняем роль напрямую в БД
    with app.app_context():
        user = db.session.query(User).filter_by(tag="moder_tag").first()
        update_user_role(user.id, "moderator")
    
    return client


@pytest.fixture
def auth_admin_client(app):
    client = app.test_client()
    client.post("/register", data={
        "username": "Admin_username",
        "tag": "admin_tag",
        "password": "admin_password",
    })
    client.post("/login", data={
        "tag": "admin_tag",
        "password": "admin_password",
    })
    
    # Меняем роль напрямую в БД
    with app.app_context():
        user = db.session.query(User).filter_by(tag="admin_tag").first()
        update_user_role(user.id, "admin")
    
    return client
