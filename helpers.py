from datetime import date

from flask import abort
from flask_login import current_user

from models import APPROVAL_STEPS, Request


def paginate_query(query, page, per_page):
    page = max(1, page)
    total = query.count()
    pages = max(1, (total + per_page - 1) // per_page)
    if page > pages:
        page = pages
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return {
        "items": items,
        "page": page,
        "pages": pages,
        "total": total,
        "per_page": per_page,
        "has_prev": page > 1,
        "has_next": page < pages,
    }


def can_view_request(user, req):
    if user.role == "admin":
        return True
    if user.role == "requester":
        return req.created_by_id == user.id
    if user.role == "security":
        return req.status == "approved"
    if user.role in APPROVAL_STEPS:
        if req.status == "pending" and req.current_step == user.role:
            return True
        if any(a.approver_role == user.role for a in req.approvals):
            return True
        if req.status in ("approved", "rejected"):
            return True
    return False


def require_request_access(req):
    if not can_view_request(current_user, req):
        abort(403)


def is_permit_valid_today(req):
    today = date.today()
    return req.start_date <= today <= req.end_date


def format_date(value):
    if not value:
        return "-"
    return value.strftime("%d/%m/%Y")


def format_datetime(value):
    if not value:
        return "-"
    return value.strftime("%d/%m/%Y %H:%M")
