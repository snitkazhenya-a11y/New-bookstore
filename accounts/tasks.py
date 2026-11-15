from celery import shared_task
from django.contrib.sessions.models import Session
from django.utils import timezone

@shared_task
def cleanup_expired_sessions():
    """Видаляє прострочені сесії користувачів із бази даних"""
    Session.objects.filter(expire_date__lt=timezone.now()).delete()
    return "Expired sessions cleaned up successfully."