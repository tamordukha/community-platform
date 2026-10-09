from models.public import get_member
from models.block import is_blocked

# Posts
def can_view_post(user, post) -> bool:
    if user:
        if user.role in ("moderator", "admin"):
            return True
        
        if user.id == post.author_id:
            return True
    
        if post.public_id and is_blocked("public", post.public_id, "user", user.id):
            return False

        if post.author_id and is_blocked("user", post.author_id, "user", user.id):
            return False
    
    if post.is_public:
        return True
    
    if not user:
        return False

    return False


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


def can_interact_with_post(user, post) -> bool:
    if not user:
        return False
    
    if post.author_id:
        if is_blocked("user", user.id, "user", post.author_id):
            return False
        if is_blocked("user", post.author_id, "user", user.id):
            return False
    
    if post.public_id:
        if is_blocked("user", user.id, "public", post.public_id):
            return False
        if is_blocked("public", post.public_id, "user", user.id):
            return False
    
    return True
    

# Comments and Replies

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


def can_delete_content(user, content, post) -> bool:
    if not user:
        return False

    if post.public_id:
        member = get_member(user.id, post.public_id)
        return member and member.role == "owner"
    
    return user.id == content.author_id or user.role in ("moderator", "admin")


def can_hide_content(user, content, post) -> bool:
    if not user:
        return False

    if user.id == content.author_id:
        return False
    
    if user.role in ("moderator", "admin"):
        return True
    
    if post.public_id:
        member = get_member(user.id, post.public_id)
        return member and member.role in ("admin", "owner")
    
    return user.id == post.author_id


# Public

def can_view_public(current_user, public) -> bool:
    if not current_user or not public:
        return False

    if current_user.role in ("moderator", "admin"):
        return True
    
    return is_blocked("public", public.id, "user", current_user.id)


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
    
    return member.role == "owner"


def can_change_member_role(current_member, member, new_role, owners_count) -> bool:
    if not current_member or not member:
        return False
    
    if member.role == new_role:
        return False

    if current_member.role == "admin" and member.role == "member" and new_role == "admin":
        return True

    if member.role == "owner" and owners_count <= 1:
        return False
    
    if current_member.role == "owner" and member.role != "owner":
        return True

    if current_member.id == member.id:
        if member.role == "member" and new_role in ("admin", "owner"):
            return False

        if member.role == "admin" and new_role == "owner":
            return False

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


def can_interact_with_public(current_user, public) -> bool:
    if not current_user or not public:
        return False
    
    if is_blocked("user", current_user.id, "public", public.id):
        return False
    if is_blocked("public", public.id, "user", current_user.id):
        return False

    return True



# Profile

def can_view_profile(current_user, profile_user) -> bool:
    if not current_user or not profile_user:
        return False

    if current_user.id == profile_user.id:
        return True

    if current_user.role in ("moderator", "admin"):
        return True
    
    return is_blocked("user", profile_user.id, "user", current_user.id)


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


def can_interact_with_profile(current_user, profile_user) -> bool:
    if not current_user or not profile_user:
        return False

    if current_user.id == profile_user.id:
        return True
    
    if is_blocked("user", current_user.id, "user", profile_user.id):
        return False
    if is_blocked("user", profile_user.id, "user", current_user.id):
        return False

    return True


# Block

def can_block_user(blocker, blocked) -> bool:
    if not blocker or not blocked:
        return False
    
    if blocker.id == blocked.id:
        return False
    
    return True
    

def can_block_member(current_member, user, member=None) -> bool:
    if not current_member or not user:
        return False
    
    if current_member.user_id == user.id:
        return False

    if current_member.role == "member":
        return False

    if member:
        if member.role == "owner":
            return False
        if current_member.role == "admin" and member.role == "admin":
            return False
    
    return True