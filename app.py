from flask import Flask, session, redirect, url_for
from config import Config
from database.db import db, init_db
from flask_wtf.csrf import CSRFProtect

from models.user import get_user_by_id

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)
    CSRFProtect(app)
    register_routes(app)
    return app

def register_routes(app):
    from routes.auth import auth_bp
    from routes.posts import posts_bp
    from routes.comments import comments_bp
    from routes.replies import replies_bp
    from routes.likes import likes_bp
    from routes.profiles import profiles_bp
    from routes.api import api_bp
    from routes.follows import follows_bp
    from routes.publics import publics_bp
    from routes.reposts import reposts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(replies_bp)
    app.register_blueprint(likes_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(follows_bp)
    app.register_blueprint(publics_bp)
    app.register_blueprint(reposts_bp)

app = create_app()

@app.before_request
def check_banned_user():
    user_id = session.get("user_id")
    if user_id:
        user = get_user_by_id(user_id)
        if user and user.is_banned:
            session.clear()
            return redirect(url_for("auth.login"))

if __name__ == "__main__":
    app.run()