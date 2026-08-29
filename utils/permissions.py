from models.public import get_member

# Posts
def can_view_post(user, post) -> bool:
    if post.is_public:
        return True
    
    if post.public_id:
        return True
    
    if not user:
        return False
    
    return user.id == post.author_id or user.role in ("moderator", "admin")


def can_edit_post(user, post) -> bool:
    if not user:
        return False
    
    if user.role == "admin":
        return True
    
    if post.public_id:
        member = get_member(user.id, post.public_id)
        return member and member.role in ("admin", "owner")
    
    return user.id == post.author_id


def can_delete_post(user, post) -> bool:
    if not user:
        return False

    if user.role in ("moderator", "admin"):
        return True

    if post.public_id:
        member = get_member(user.id, post.public_id)
        return member and member.role in ("admin", "owner")

    return user.id == post.author_id


# Comments

def can_view_content(user, post, content) -> bool:
    if not content.is_hidden:
        return True
    
    return user.id == post.author_id or user.role in ("moderator", "admin")


def can_edit_content(user, content) -> bool:
    if not user:
        return False
    
    if user.role == "admin":
        return True
    
    return user.id == content.author_id


def can_delete_content(user, content) -> bool:
    if not user:
        return False
    
    return user.id == content.author_id or user.role in ("moderator", "admin")


def can_hide_content(user, post) -> bool:
    if not user:
        return False
    
    if user.role in ("moderator", "admin"):
        return True
    
    if post.public_id:
        member = get_member(user.id, post.public_id)
        return member and member.role in ("admin", "owner")
    
    return user.id == post.author_id


# Public

def can_edit_public(member, public) -> bool:
    if not member:
        return False
    
    if member.public_id != public.id:
        return False
    
    return member.role in ("admin", "owner")


def can_delete_public(member, public) -> bool:
    if not member:
        return False
    
    if member.public_id != public.id:
        return False
    
    return member.role == "onwer"


def can_change_member_role(current_member, member, new_role) -> bool:
    if not current_member or not member:
        return False
    
    if current_member.id == member.id or member.role == new_role:
        return False
    
    if current_member.role == "admin" and member.role == "member" and new_role == "admin":
        return True
    
    if current_member.role == "owner" and member.role != "owner":
        return True
    
    return False


def can_kick_member(current_member, member) -> bool:
    if not current_member or not member:
        return False
    
    if current_member.id == member.id:
        return False
    
    if current_member.role == "admin" and member.role == "member":
        return True
    
    if current_member.role == "owner" and member.role != "owner":
        return True
    
    return False


# Profile

def can_change_role(current_user, profile_user, new_role) -> bool:
    if not current_user or not profile_user:
        return False
    
    if current_user.id == profile_user.id or profile_user.role == new_role:
        return False
    
    if current_user.role == "moderator" and profile_user.role == "user" and new_role == "moderator":
        return True
    
    if current_user.role == "admin" and profile_user.role != "admin":
        return True
    
    return False


def can_modify_role(current_user, profile_user) -> bool:
    if not current_user or not profile_user:
        return False
    
    if current_user.id == profile_user.id:
        return False
    
    if current_user.role == "admin" and profile_user.role != "admin":
        return True
    
    if current_user.role == "moderator" and profile_user.role == "user":
        return True
    
    return False


# Block

def can_block_user(blocker, blocked) -> bool:
    if not blocker or not blocked:
        return False
    
    if blocker.id == blocked.id:
        return False
    
    if blocker.role == "admin" and blocked.role != "admin":
        return True
    
    if blocker.role == "moderator" and blocked.role == "user":
        return True
    
    return False