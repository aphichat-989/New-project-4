from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from config import Config
from helpers import format_date, is_permit_valid_today, paginate_query
from i18n import _
from models import Request, SecurityLog, db
from routes.decorators import role_required

security_bp = Blueprint("security", __name__)


@security_bp.route("/security")
@login_required
@role_required("security", "admin")
def checkin():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    today_only = request.args.get("today", "1") == "1"

    query = Request.query.filter_by(status="approved")
    if today_only:
        today = date.today()
        query = query.filter(Request.start_date <= today, Request.end_date >= today)

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Request.request_no.ilike(like),
                Request.requester_name.ilike(like),
            )
        )
    query = query.order_by(Request.start_date.desc())
    pagination = paginate_query(query, page, Config.ITEMS_PER_PAGE)

    items_with_validity = [
        {"item": item, "valid_today": is_permit_valid_today(item)}
        for item in pagination["items"]
    ]

    return render_template(
        "security_checkin.html",
        items=items_with_validity,
        pagination=pagination,
        q=q,
        today_only=today_only,
    )


@security_bp.route("/security/<int:request_id>", methods=["POST"])
@login_required
@role_required("security", "admin")
def log_action(request_id):
    req = db.session.get(Request, request_id)
    if not req:
        return redirect(url_for("security.checkin"))

    if req.status != "approved":
        flash(_("flash.not_approved"), "warning")
        return redirect(url_for("security.checkin"))

    if not is_permit_valid_today(req) and current_user.role != "admin":
        flash(
            _("flash.outside_dates", start=format_date(req.start_date), end=format_date(req.end_date)),
            "danger",
        )
        return redirect(url_for("security.checkin"))

    action = request.form.get("action")
    note = request.form.get("note", "").strip()
    if action not in ("check_in", "check_out"):
        flash(_("flash.choose_action"), "warning")
        return redirect(url_for("security.checkin"))

    log = SecurityLog(
        request_id=req.id,
        guard_name=current_user.full_name,
        action=action,
        note=note,
    )
    db.session.add(log)
    db.session.commit()

    if action == "check_in":
        flash(_("flash.check_in_ok", no=req.request_no), "success")
    else:
        flash(_("flash.check_out_ok", no=req.request_no), "success")
    return redirect(url_for("security.checkin"))
