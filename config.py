import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-before-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    FACTORY_NAME = os.environ.get("FACTORY_NAME", "Work Permit System")
    FACTORY_NAME_TH = os.environ.get("FACTORY_NAME_TH", "ระบบใบอนุญาตเข้า-ออกพื้นที่")
    FACTORY_NAME_ZH = os.environ.get("FACTORY_NAME_ZH", "工作许可系统")

    DEFAULT_LOCALE = os.environ.get("DEFAULT_LOCALE", "th")
    TIMEZONE = os.environ.get("TIMEZONE", "Asia/Bangkok")
    ITEMS_PER_PAGE = int(os.environ.get("ITEMS_PER_PAGE", "20"))

    SEED_DEMO_DATA = os.environ.get("SEED_DEMO_DATA", "true").lower() == "true"
    SHOW_DEMO_ACCOUNTS = os.environ.get("SHOW_DEMO_ACCOUNTS", "true").lower() == "true"

    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    HOST = os.environ.get("FLASK_HOST", "127.0.0.1")
    PORT = int(os.environ.get("FLASK_PORT", "5000"))

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
