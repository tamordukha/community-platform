# Posts
def can_view_post(user, post):
    if post.is_public:
        return True
    if not user:
        return False
    return user.id == post.author_id or user.role in ("moderator", "admin")

def can_edit_post(user, post):
    if not user:
        return False
    return user.id == post.author_id or user.role == "admin"

def can_delete_post(user, post):
    if not user:
        return False
    return user.id == post.author_id or user.role in ("moderator", "admin")

# Comments
def can_view_comment(user, post, comment):
    if not comment.is_hidden:
        return True
    return user.id == post.author_id or user.role in ("moderator", "admin")

def can_edit_comment(user, comment):
    if not user:
        return False
    return user.id == comment.author_id or user.role == "admin"

def can_delete_comment(user, comment):
    if not user:
        return False
    return user.id == comment.author_id or user.role in ("moderator", "admin")

def can_hide_comment(user, post):
    if not user:
        return False
    return user.id == post.author_id or user.role in ("moderator", "admin")

# Replies
def can_view_reply(user, post, reply):
    if not reply.is_hidden:
        return True
    return user.id == post.author_id or user.role in ("moderator", "admin")

def can_edit_reply(user, reply):
    if not user:
        return False
    return user.id == reply.author_id or user.role == "admin"

def can_delete_reply(user, reply):
    if not user:
        return False
    return user.id == reply.author_id or user.role in ("moderator", "admin")

def can_hide_reply(user, post):
    if not user:
        return False
    return user.id == post.author_id or user.role in ("moderator", "admin")

# Profile
def can_change_role(current_user, profile_user, new_role):
    if current_user is None:
        return False
    if current_user["id"] == profile_user["id"] or profile_user["role"] == new_role:
        return False
    if current_user["role"]=="moderator" and profile_user["role"]=="user" and new_role=="moderator":
        return True
    if current_user["role"] == "admin" and profile_user["role"] != "admin":
        return True
    return False

def can_modify_role(current_user, profile_user):
    if current_user is None:
        return False
    if current_user["id"] == profile_user["id"]:
        return False
    if current_user["role"] == "admin" and profile_user["role"] != "admin":
        return True
    if current_user["role"] == "moderator" and profile_user["role"] == "user":
        return True
    return False