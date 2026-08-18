def can_view_post(user, post):
    if post.is_public:
        return True
    if not user:
        return False
    return user.id == post.author_id or user.role in ("moderator", "admin")