#Posts
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

#Comments
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

def can_hide_comment(user, post, comment):
    if not user:
        return False
    return user.id == post.author_id or user.role in ("moderator", "admin")