# core/views.py
from django.http import JsonResponse
from django.db import connection
import redis
from django.conf import settings


def health_check(request):
    health_data = {"status": "healthy"}

    # Перевірка бази даних
    try:
        connection.ensure_connection()
        health_data["database"] = "connected"
    except Exception as e:
        health_data["database"] = f"error: {str(e)}"
        health_data["status"] = "unhealthy"

    # Перевірка Redis
    try:
        r = redis.from_url(settings.CACHES["default"]["LOCATION"])
        r.ping()
        health_data["redis"] = "connected"
    except Exception as e:
        health_data["redis"] = f"error: {str(e)}"
        health_data["status"] = "unhealthy"

    status_code = 200 if health_data["status"] == "healthy" else 503
    return JsonResponse(health_data, status=status_code)
