from datetime import datetime, UTC
from database.db import db
from models.user import get_user_by_tag
from models.public import Public, PublicMember, get_public_by_id, get_member_by_id

class Block(db.Model):
    __tablename__ = "blocks"

    id = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer)
    blocked_id = db.Column(db.Integer)
    blocker_type = db.Column(db.String(20))
    blocked_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    __table_args__ = (db.UniqueConstraint('blocker_id', 'blocked_id', name='unique_block'),)


def toggle_block(blocker_type, blocker_id, blocked_type, blocked_id):
    block = db.session.query(Block).filter_by(blocker_id=blocker_id,
                                            blocked_id=blocked_id,
                                            blocker_type=blocker_type,
                                            blocked_type=blocked_type).first()
    if block:
        db.session.delete(block)
    else:
        Block(blocker_id=blocker_id,
            blocked_id=blocked_id,
            blocker_type=blocker_type,
            blocked_type=blocked_type)
        db.session.add(block)
        
    db.session.commit()
    
def is_blocked(blocker_type, blocker_id, blocked_type, blocked_id):
    block = db.session.query(Block).filter_by(blocker_id=blocker_id,
                                            blocked_id=blocked_id,
                                            blocker_type=blocker_type,
                                            blocked_type=blocked_type).first()
    return block is not None