from datetime import datetime, UTC
from database.db import db
from models.user import get_user_by_id
from models.public import get_public_by_id
from models.post import get_post
from models.comment import get_comment
from models.reply import get_reply

class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    source_type = db.Column(db.String(20), nullable=False)  # user/public/post/comment/reply
    source_id = db.Column(db.Integer, nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # user/public
    target_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    is_pending = db.Column(db.Boolean, default=True, nullable=False)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    __table_args__ = (db.UniqueConstraint('reporter_id', 'source_type', 'source_id', name='unique_report'),)


def add_report(source_id, source_type, target_id, target_type, reporter_id, reason):
    if is_reported(source_id, source_type, reporter_id):
        return None

    report = Report(
        source_id = source_id,
        source_type = source_type,
        target_id   = target_id,
        target_type = target_type,
        reporter_id = reporter_id,
        reason      = reason,
        is_pending  = True
    )

    db.session.add(report)
    db.session.commit()


def dismiss_report(report_id, resolved_by):
    report = db.session.get(Report, report_id)
    if report and report.is_pending:
        report.is_pending = False
        report.resolved_by = resolved_by
        report.resolved_at = datetime.now(UTC)
        db.session.commit()


def is_reported(source_id, source_type, reporter_id):
    report = db.session.query(Report).filter_by(source_id=source_id, source_type=source_type, reporter_id=reporter_id, is_pending=True).first()
    return report is not None


def get_report(report_id):
    return db.session.get(Report, report_id)


def get_filter_reports(
    source_id=None, source_type=None,
    target_id=None, target_type=None,
    reporter_id=None, resolved_by=None,
    is_pending=None, ascending=False,
    limit=50, offset=0
    ):
    query = db.session.query(Report)

    if source_id and source_type:
        query = query.filter_by(source_id=source_id, source_type=source_type)

    if target_id and target_type:
        query = query.filter_by(target_id=target_id, target_type=target_type)

    if reporter_id:
        query = query.filter_by(reporter_id=reporter_id)

    if resolved_by:
        query = query.filter_by(reporter_id=reporter_id)

    if is_pending is not None:
        query = query.filter_by(is_pending=is_pending)

    reports = query.offset(offset).limit(limit).all()
    
    if ascending:
        return reports.reverse()

    return reports


def get_object(object_type, object_id):
    if object_type == "user":
        return (get_user_by_id(object_id), object_type)
    if object_type == "public":
        return (get_public_by_id(object_id), object_type)
    if object_type == "post":
        return (get_post(object_id), object_type)
    if object_type == "comment":
        return (get_comment(object_id), object_type)
    if object_type == "reply":
        return (get_reply(object_id), object_type)
    return None