import pytest
import os
import tempfile
from app import create_app
from database.db import db, init_db

from models import *

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

    with app.app_context():
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


# Clients

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(app):
    client = app.test_client()
    client.post("/register", data={
        "username": "username",
        "tag": "user_tag",
        "password": "Password1",
    })
    client.post("/login", data={
        "tag": "user_tag",
        "password": "Password1",
    })
    return client


@pytest.fixture
def auth_foreign_client(app):
    client = app.test_client()

    client.post("/register", data={
        "username": "username",
        "tag": "user_tag2",
        "password": "Password1",
    })

    client.post("/login", data={
        "tag": "user_tag2",
        "password": "Password1",
    })
    
    return client


@pytest.fixture
def auth_mod_client(app):
    client = app.test_client()

    client.post("/register", data={
        "username": "moder_username",
        "tag": "moder_tag",
        "password": "Password1",
    })

    client.post("/login", data={
        "tag": "moder_tag",
        "password": "Password1",
    })
    
    # Меняем роль напрямую в БД
    with app.app_context():
        user = db.session.query(User).filter_by(tag="moder_tag").first()
        user.role = "moderator"

        db.session.commit()

    client.get("/logout")
    client.post("/login", data={"tag": "moder_tag", "password": "Password1"})

    return client


@pytest.fixture
def auth_admin_client(app):
    client = app.test_client()

    client.post("/register", data={
        "username": "admin_username",
        "tag": "admin_tag",
        "password": "Password1",
    })

    client.post("/login", data={
        "tag": "admin_tag",
        "password": "Password1",
    })
    
    # Меняем роль напрямую в БД
    with app.app_context():
        user = db.session.query(User).filter_by(tag="admin_tag").first()
        user.role = "admin"

        db.session.commit()

    client.get("/logout")
    client.post("/login", data={"tag": "admin_tag", "password": "Password1"})
    
    return client


# Posts

@pytest.fixture
def create_post():
    def _create(client, content="post content", is_public=1):
        return client.post("/post/create", data={
            "content": content,
            "is_public": is_public,
        })
    return _create


# Comments

@pytest.fixture
def create_comment(create_post):
    def _create(client, content="comment content", is_public=1):
        create_post(client, is_public=is_public)

        return client.post("/post/1/comment/create", data={
            "content": content,
        })
    
    return _create