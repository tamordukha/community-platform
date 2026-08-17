from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Создаём объект SQLAlchemy (без привязки к app)
db = SQLAlchemy()

# Создаём объект для миграций
migrate = Migrate()

def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Создаём таблицы (для разработки)
    with app.app_context():
        db.create_all()