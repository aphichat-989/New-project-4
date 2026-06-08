from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

from i18n import _


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            allowed = set(roles) | {"admin"}
            if current_user.role not in allowed:
                flash(_("flash.no_access"), "danger")
                return redirect(url_for("dashboard.index"))
            return f(*args, **kwargs)

        return wrapped

    return decorator
