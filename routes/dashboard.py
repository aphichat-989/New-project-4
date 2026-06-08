from flask import Blueprint, render_template
from flask_login import current_user, login_required

from config import Config
from models import Request

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    if current_user.role == "requester":
        my_requests = Request.query.filter_by(created_by_id=current_user.id).all()
        pending = [r for r in my_requests if r.status == "pending"]
        approved = [r for r in my_requests if r.status == "approved"]
        stats = {
            "total": len(my_requests),
            "pending": len(pending),
            "approved": len(approved),
            "rejected": len([r for r in my_requests if r.status == "rejected"]),
        }
    elif current_user.role == "security":
        stats = {
            "total": Request.query.filter_by(status="approved").count(),
            "pending": 0,
            "approved": Request.query.filter_by(status="approved").count(),
            "rejected": 0,
        }
    elif current_user.role == "admin":
        stats = {
            "total": Request.query.count(),
            "pending": Request.query.filter_by(status="pending").count(),
            "approved": Request.query.filter_by(status="approved").count(),
            "rejected": Request.query.filter_by(status="rejected").count(),
        }
    else:
        waiting = Request.query.filter_by(
            status="pending", current_step=current_user.role
        ).count()
        stats = {
            "total": Request.query.count(),
            "pending": waiting,
            "approved": Request.query.filter_by(status="approved").count(),
            "rejected": Request.query.filter_by(status="rejected").count(),
        }

    recent = Request.query.order_by(Request.created_at.desc()).limit(8).all()
    return render_template("dashboard.html", stats=stats, recent=recent)
