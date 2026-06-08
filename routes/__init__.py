from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.requests import requests_bp
from routes.approvals import approvals_bp
from routes.security import security_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(approvals_bp)
    app.register_blueprint(security_bp)
