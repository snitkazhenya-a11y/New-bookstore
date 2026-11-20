import os
from .base import *

DEBUG = False

raw_hosts = os.environ.get("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [host.strip() for host in raw_hosts.split(",") if host.strip()]

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = (
    os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"
)
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "False").lower() == "true"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Підключення до БД через DATABASE_URL, якщо передано в середовищі
if os.environ.get("DATABASE_URL"):
    import dj_database_url

    DATABASES["default"] = dj_database_url.config(
        default=os.environ["DATABASE_URL"],
        conn_max_age=600,
    )

# Підключення до Redis через REDIS_URL, якщо передано в середовищі
if os.environ.get("REDIS_URL"):
    redis_url = os.environ["REDIS_URL"]
    CACHES["default"]["LOCATION"] = redis_url
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", redis_url)
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", redis_url)
