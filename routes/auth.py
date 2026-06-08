from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user

from i18n import SUPPORTED_LOCALES, _
from models import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.locale in SUPPORTED_LOCALES:
                session["locale"] = user.locale
            flash(_("flash.welcome", name=user.full_name), "success")
            return redirect(url_for("dashboard.index"))
        flash(_("flash.login_fail"), "danger")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash(_("flash.logout"), "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/set-language/<lang>")
def set_language(lang):
    if lang in SUPPORTED_LOCALES:
        session["locale"] = lang
        if current_user.is_authenticated:
            current_user.locale = lang
            db.session.commit()
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))
