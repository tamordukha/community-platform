from datetime import datetime, UTC

def calculate_post_score(post):
    likes = post.likes.count()
    comments = post.comments.count()
    time_diff = datetime.now(UTC) - post.created_at
    age_hours = int(time_diff.total_seconds() / 3600)
    return (likes * 2) + (comments * 3) + (1 / (age_hours + 1))