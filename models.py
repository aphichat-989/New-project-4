from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

APPROVAL_STEPS = [
    "specialist",
    "assistant_manager",
    "dgm",
    "hr",
]


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    department = db.Column(db.String(100))
    locale = db.Column(db.String(5), default="th")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def role_label(self):
        from i18n import t_role

        return t_role(self.role)


class Request(db.Model):
    __tablename__ = "requests"

    id = db.Column(db.Integer, primary_key=True)
    request_no = db.Column(db.String(30), unique=True, nullable=False)
    requester_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(150))
    contact_phone = db.Column(db.String(30))
    permit_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    work_area = db.Column(db.String(50), nullable=False)
    work_area_detail = db.Column(db.String(200))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="pending")
    current_step = db.Column(db.String(30), default="specialist")
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    created_by = db.relationship("User", backref="requests")
    approvals = db.relationship(
        "Approval", backref="request", lazy=True, order_by="Approval.approved_at"
    )
    images = db.relationship(
        "RequestImage", backref="request", lazy=True, order_by="RequestImage.uploaded_at"
    )

    security_logs = db.relationship(
        "SecurityLog", backref="request", lazy=True, order_by="SecurityLog.logged_at"
    )

    @property
    def status_badge(self):
        if self.status == "approved":
            return "success"
        if self.status == "rejected":
            return "danger"
        return "warning"

    @property
    def status_label(self):
        from i18n import t_status

        return t_status(self.status)

    @property
    def current_step_label(self):
        from i18n import t_step

        return t_step(self.current_step, self.status)

    @property
    def permit_type_label(self):
        from i18n import t_permit

        return t_permit(self.permit_type)

    @property
    def work_zone_label(self):
        from i18n import t_zone

        return t_zone(self.work_area)

    @property
    def zone_display(self):
        label = self.work_zone_label
        if self.work_area_detail:
            return f"{label} — {self.work_area_detail}"
        return label

    def can_approve(self, user):
        if self.status != "pending":
            return False
        if user.role == "admin":
            return True
        return user.role == self.current_step


class Approval(db.Model):
    __tablename__ = "approvals"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    approver_role = db.Column(db.String(30), nullable=False)
    approver_name = db.Column(db.String(100), nullable=False)
    decision = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text)
    approved_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def role_label(self):
        from i18n import t_role

        return t_role(self.approver_role)

    @property
    def decision_label(self):
        from i18n import t_decision

        return t_decision(self.decision)


class RequestImage(db.Model):
    __tablename__ = "request_images"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class SecurityLog(db.Model):
    __tablename__ = "security_logs"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    guard_name = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def action_label(self):
        from i18n import t_action

        return t_action(self.action)
