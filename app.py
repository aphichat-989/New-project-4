import os
from datetime import date, timedelta

from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import inspect, text

from config import Config
from factory_data import DEPARTMENT_CODES, PERMIT_TYPE_CODES, WORK_ZONE_CODES
from i18n import (
    SUPPORTED_LOCALES,
    _,
    factory_name,
    get_locale,
    t_action,
    t_decision,
    t_dept,
    t_permit,
    t_role,
    t_status,
    t_step,
    t_zone,
)
from models import Request, User, db
from routes import register_blueprints
from utils import generate_request_no

csrf = CSRFProtect()


def ensure_schema():
    inspector = inspect(db.engine)
    if "users" in inspector.get_table_names():
        user_cols = {c["name"] for c in inspector.get_columns("users")}
        if "locale" not in user_cols:
            db.session.execute(text("ALTER TABLE users ADD COLUMN locale VARCHAR(5) DEFAULT 'th'"))
            db.session.commit()

    if "requests" in inspector.get_table_names():
        req_cols = {c["name"] for c in inspector.get_columns("requests")}
        migrations = [
            ("company_name", "VARCHAR(150)"),
            ("contact_phone", "VARCHAR(30)"),
            ("work_area_detail", "VARCHAR(200)"),
        ]
        for col, col_type in migrations:
            if col not in req_cols:
                db.session.execute(
                    text(f"ALTER TABLE requests ADD COLUMN {col} {col_type}")
                )
        db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "requests"), exist_ok=True)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_globals():
        return {
            "_": _,
            "get_locale": get_locale,
            "LANGUAGES": SUPPORTED_LOCALES,
            "factory_name": factory_name,
            "t_status": t_status,
            "t_role": t_role,
            "t_step": t_step,
            "t_permit": t_permit,
            "t_zone": t_zone,
            "t_dept": t_dept,
            "t_decision": t_decision,
            "t_action": t_action,
            "APPROVAL_STEPS": __import__("models", fromlist=["APPROVAL_STEPS"]).APPROVAL_STEPS,
            "SHOW_DEMO_ACCOUNTS": Config.SHOW_DEMO_ACCOUNTS,
            "DEPARTMENT_CODES": DEPARTMENT_CODES,
            "PERMIT_TYPE_CODES": PERMIT_TYPE_CODES,
            "WORK_ZONE_CODES": WORK_ZONE_CODES,
        }

    register_blueprints(app)

    @app.errorhandler(403)
    def forbidden(_e):
        from flask import flash, redirect, url_for
        from flask_login import current_user

        flash(_("common.access_denied"), "danger")
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))

    with app.app_context():
        db.create_all()
        ensure_schema()
        if Config.SEED_DEMO_DATA:
            seed_sample_data()

    return app


def seed_sample_data():
    if User.query.first():
        return

    users = [
        ("requester1", "ผู้ขอ ทดสอบ", "requester", "production", "password"),
        ("specialist1", "สมชาย Specialist", "specialist", "engineering", "password"),
        ("asst_mgr1", "สมหญิง Assistant Manager", "assistant_manager", "engineering", "password"),
        ("dgm1", "สมศักดิ์ DGM", "dgm", "engineering", "password"),
        ("hr1", "สมใจ HR", "hr", "hr", "password"),
        ("security1", "ยาม รักษาความปลอดภัย", "security", "security", "password"),
        ("admin1", "ผู้ดูแลระบบ", "admin", "it", "password"),
    ]

    for username, full_name, role, department, password in users:
        user = User(
            username=username,
            full_name=full_name,
            role=role,
            department=department,
            locale="th",
        )
        user.set_password(password)
        db.session.add(user)

    db.session.commit()

    requester = User.query.filter_by(username="requester1").first()
    sample = Request(
        request_no=generate_request_no(),
        requester_name="ผู้ขอ ทดสอบ",
        department="production",
        company_name="",
        contact_phone="081-234-5678",
        permit_type="maintenance",
        description="ซ่อมสายพานลำเลียงสายที่ 2 — ตรวจสอบ PPE ก่อนเข้าพื้นที่",
        work_area="zone_a",
        work_area_detail="สายพาน Line 2",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=3),
        status="pending",
        current_step="specialist",
        created_by_id=requester.id,
    )
    db.session.add(sample)
    db.session.commit()


if __name__ == "__main__":
    application = create_app()
    print("=" * 50)
    print(factory_name())
    print(f"http://{Config.HOST}:{Config.PORT}")
    if Config.SHOW_DEMO_ACCOUNTS:
        print("Demo password: password")
    print("=" * 50)
    application.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
