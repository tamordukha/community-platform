import string
import magic
from config import Config

def is_valid_tag(tag):
    if not tag or len(tag) < 3 or len(tag) > 20:
        return False
    if tag[0] in string.digits:
        return False
    return all(char in string.ascii_lowercase + string.digits + "_" for char in tag)

def is_valid_username(username):
    if not username or len(username) < 2 or len(username) > 40:
        return False
    return True

def is_valid_password(password):
    if not password or len(password) < 6 or len(password) > 128:
        return False
    return any(char in string.ascii_uppercase + string.digits for char in password)

def is_valid_bio(description):
    if description > Config.BIO_MAX_LENGTH:
        return False
    return True

def validate_image(file):
    filename = file.filename
    
    # Проверка расширения
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in Config.ALLOWED_IMAGE_TYPES:
        return False
    
    # Проверка MIME
    file_head = file.read(2048)
    file.seek(0)
    
    mime_detector = magic.Magic(mime=True)
    real_mime = mime_detector.from_buffer(file_head)
    
    if real_mime not in Config.ALLOWED_MIME_TYPES:
        return False
    
    return True