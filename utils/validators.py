import string

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