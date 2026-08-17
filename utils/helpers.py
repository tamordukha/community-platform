import random
import string
from models.user import User

def generate_unique_tag(username):
    # Оставляет только английские буквы, цифры, пробелы, подчёркивания
    base = ''.join(
        char for char in username.lower().strip().replace(" ", "_")[:20]
        if char in string.ascii_lowercase + string.digits + "_"
    )
    
    if not base:
        base = "user"
    
    tag = base
    while User.query.filter_by(tag=tag).first():
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        tag = f"{base[:17]}_{suffix}"
    
    return tag