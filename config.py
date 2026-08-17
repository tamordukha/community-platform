import os
from dotenv import load_dotenv

load_dotenv()  # Загрузка .env файла

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    
    # База данных
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", 
        f"sqlite:///{os.path.join(BASEDIR, 'community.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Проверка соединения перед запросом
    }
    
    # Куки
    SESSION_COOKIE_HTTPONLY = True   # Защита от XSS
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"    # автоматически станет True на продакшене (HTTPS)
    SESSION_COOKIE_SAMESITE = "Lax"  # Защита от CSRF
    
    # Загрузка файлов
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB максимум
    UPLOAD_FOLDER = os.path.join(BASEDIR, "static", "uploads")
    
    # Подпапки для разных типов
    AVATAR_FOLDER = os.path.join(UPLOAD_FOLDER, "avatars")
    BANNER_FOLDER = os.path.join(UPLOAD_FOLDER, "banners")
    POST_IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "posts")
    COMMENT_IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "comments")
    
    # Разрешённые типы файлов
    ALLOWED_IMAGE_TYPES = frozenset({"png", "jpeg", "jpg", "gif"})
    ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/gif"}
    
    # Лимиты контента
    POST_MAX_LENGTH = 2000
    COMMENT_MAX_LENGTH = 500
    REPLY_MAX_LENGTH = 500
    BIO_MAX_LENGTH = 150
    
    # Пагинация
    POSTS_PER_PAGE = 20
    COMMENTS_PER_PAGE = 30
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_STORAGE_URI = "memory://"  # Для продакшена: redis://