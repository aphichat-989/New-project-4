from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from config import Config
from helpers import format_date, paginate_query
from i18n import _
from models import Request, db
from routes.decorators import role_required
from utils import process_approval

approvals_bp = Blueprint("approvals", __name__)


@approvals_bp.route("/approvals")
@login_required
@role_required(
    "specialist",
    "assistant_manager",
    "dgm",
    "hr",
    "admin",
)
def index():
    page = request.args.get("page", 1, type=int)
    if current_user.role == "admin":
        query = Request.query.filter_by(status="pending")
    else:
        query = Request.query.filter_by(
            status="pending", current_step=current_user.role
        )
    query = query.order_by(Request.created_at.asc())
    pagination = paginate_query(query, page, Config.ITEMS_PER_PAGE)
    return render_template("approval.html", items=pagination["items"], pagination=pagination)


@approvals_bp.route("/approvals/<int:request_id>", methods=["POST"])
@login_required
@role_required(
    "specialist",
    "assistant_manager",
    "dgm",
    "hr",
    "admin",
)
def decide(request_id):
    req = db.session.get(Request, request_id)
    if not req:
        return redirect(url_for("approvals.index"))

    if not req.can_approve(current_user):
        flash(_("flash.cannot_approve"), "danger")
        return redirect(url_for("approvals.index"))

    decision = request.form.get("decision")
    comment = request.form.get("comment", "").strip()

    if decision not in ("approved", "rejected"):
        flash(_("flash.choose_decision"), "warning")
        return redirect(url_for("requests.detail", request_id=req.id))

    process_approval(req, current_user, decision, comment)
    if decision == "approved":
        flash(_("flash.approved", no=req.request_no), "success")
    else:
        flash(_("flash.rejected", no=req.request_no), "success")
    return redirect(url_for("approvals.index"))
