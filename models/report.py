from datetime import datetime, UTC
from database.db import db

class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # user/public
    target_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    is_pending = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    __table_args__ = (db.UniqueConstraint('reporter_id', 'target_type', 'target_id', name='unique_report'),)


def add_report(target_id, target_type, reporter_id, reason):
    if is_reported(target_id, target_type, reporter_id):
        return None

    report = Report(
        target_id   = target_id,
        target_type = target_type,
        reporter_id = reporter_id,
        reason      = reason,
        is_pending  = True
    )

    db.session.add(report)
    db.session.commit()


def dismiss_report(report_id):
    report = db.session.get(Report, report_id)
    if report and report.is_pending:
        report.is_pending = False
        db.session.commit()


def is_reported(target_id, target_type, reporter_id):
    report = db.session.query(Report).filter_by(target_id=target_id, target_type=target_type, reporter_id=reporter_id, is_pending=True).first()
    return report is not None


def get_report(report_id):
    return db.session.get(Report, report_id)


def get_filter_reports(target_id=None, target_type=None, reporter_id=None, is_pending=None):
    query = db.session.query(Report)

    if target_id and target_type:
        query = query.filter_by(target_id=target_id, target_type=target_type)

    if reporter_id:
        query = query.filter_by(reporter_id=reporter_id)

    if is_pending is not None:
        query = query.filter_by(is_pending=is_pending)

    return query.all()