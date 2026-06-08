import os
from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from config import Config
from factory_data import DEPARTMENT_CODES, PERMIT_TYPE_CODES, WORK_ZONE_CODES
from helpers import can_view_request, paginate_query
from i18n import _
from models import Request, RequestImage, db
from routes.decorators import role_required
from utils import generate_request_no

requests_bp = Blueprint("requests", __name__)


def allowed_image(filename):
    return (
        filename
        and "." in filename
        and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_IMAGE_EXTENSIONS
    )


@requests_bp.route("/requests")
@login_required
def list_requests():
    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)

    query = Request.query

    if current_user.role == "requester":
        query = query.filter_by(created_by_id=current_user.id)
    elif current_user.role not in ("admin", "security"):
        if request.args.get("mine") != "all":
            query = query.filter_by(current_step=current_user.role, status="pending")

    if status_filter:
        query = query.filter_by(status=status_filter)

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Request.request_no.ilike(like),
                Request.requester_name.ilike(like),
                Request.department.ilike(like),
                Request.work_area.ilike(like),
                Request.work_area_detail.ilike(like),
                Request.company_name.ilike(like),
            )
        )

    query = query.order_by(Request.created_at.desc())
    pagination = paginate_query(query, page, Config.ITEMS_PER_PAGE)

    return render_template(
        "request_list.html",
        items=pagination["items"],
        pagination=pagination,
        q=q,
        status_filter=status_filter,
    )


@requests_bp.route("/requests/create", methods=["GET", "POST"])
@login_required
@role_required("requester", "admin")
def create():
    if request.method == "POST":
        try:
            start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
        except ValueError:
            flash(_("flash.date_invalid"), "danger")
            return render_template(
                "request_create.html",
                default=_form_defaults(),
                permit_types=PERMIT_TYPE_CODES,
                work_zones=WORK_ZONE_CODES,
                departments=DEPARTMENT_CODES,
            )

        if end_date < start_date:
            flash(_("flash.date_range"), "danger")
            return render_template(
                "request_create.html",
                default=_form_defaults(),
                permit_types=PERMIT_TYPE_CODES,
                work_zones=WORK_ZONE_CODES,
                departments=DEPARTMENT_CODES,
            )

        req = Request(
            request_no=generate_request_no(),
            requester_name=request.form["requester_name"].strip(),
            department=request.form["department"].strip(),
            company_name=request.form.get("company_name", "").strip(),
            contact_phone=request.form.get("contact_phone", "").strip(),
            permit_type=request.form["permit_type"].strip(),
            description=request.form["description"].strip(),
            work_area=request.form["work_zone"].strip(),
            work_area_detail=request.form.get("work_area_detail", "").strip(),
            start_date=start_date,
            end_date=end_date,
            status="pending",
            current_step="specialist",
            created_by_id=current_user.id,
        )
        db.session.add(req)

        images = request.files.getlist("images")
        for image in images:
            if not image or not image.filename:
                continue
            if not allowed_image(image.filename):
                flash(
                    "รองรับเฉพาะไฟล์รูปภาพ .jpg .jpeg .png .gif เท่านั้น",
                    "warning",
                )
                continue

            raw_name = secure_filename(image.filename)
            base_name, ext = os.path.splitext(raw_name)
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
            final_name = f"{req.request_no}_{timestamp}{ext.lower()}"
            upload_subdir = os.path.join(Config.UPLOAD_FOLDER, "requests")
            os.makedirs(upload_subdir, exist_ok=True)
            save_path = os.path.join(upload_subdir, final_name)
            image.save(save_path)

            req_image = RequestImage(request=req, filename=final_name)
            db.session.add(req_image)

        db.session.commit()
        flash(_("flash.request_sent", no=req.request_no), "success")
        return redirect(url_for("requests.detail", request_id=req.id))

    return render_template(
        "request_create.html",
        default=_form_defaults(),
        permit_types=PERMIT_TYPE_CODES,
        work_zones=WORK_ZONE_CODES,
        departments=DEPARTMENT_CODES,
    )


def _form_defaults():
    dept = current_user.department or ""
    if dept not in DEPARTMENT_CODES:
        dept = "production"
    return {
        "requester_name": current_user.full_name,
        "department": dept,
        "contact_phone": "",
        "company_name": "",
    }


@requests_bp.route("/requests/<int:request_id>")
@login_required
def detail(request_id):
    req = db.session.get(Request, request_id)
    if not req:
        abort(404)
    if not can_view_request(current_user, req):
        abort(403)
    return render_template("request_detail.html", req=req)
