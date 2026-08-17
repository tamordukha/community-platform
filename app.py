from flask import Flask
from config import Config
from database.db import db, init_db
from flask_wtf.csrf import CSRFProtect

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
    from routes.follow import follow_bp
    from routes.publics import publics_bp
    from routes.reposts import reposts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(replies_bp)
    app.register_blueprint(likes_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(follow_bp)
    app.register_blueprint(publics_bp)
    app.register_blueprint(reposts_bp)

app = create_app()

if __name__ == "__main__":
    app.run()