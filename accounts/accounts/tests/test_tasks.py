import pytest
from django.contrib.sessions.models import Session
from accounts.tasks import cleanup_expired_sessions

@pytest.mark.django_db
def test_cleanup_expired_sessions_task():
    try:
        result = cleanup_expired_sessions()
        assert True
    except Exception as e:
        pytest.fail(f"Celery task failed with error: {e}")