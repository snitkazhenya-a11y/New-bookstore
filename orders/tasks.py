import logging
from celery import shared_task
from django.core.mail import send_mail
from django.core.management import call_command

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_order_confirmation_email(
    self, order_id: int, customer_name: str, customer_email: str
):
    subject = f"Замовлення №{order_id}"
    message = (
        f"Вітаю, {customer_name}!\n\n"
        f"Ви успішно оформили замовлення у нашій книгарні. ID замовлення: {order_id}."
    )
    try:
        send_mail(subject, message, "from@bookstore.com", [customer_email])
        logger.info(
            "Лист про замовлення №%s відправлено на %s", order_id, customer_email
        )
    except Exception as exc:
        logger.error("Помилка відправки листа для замовлення №%s: %s", order_id, exc)
        raise self.retry(exc=exc)


@shared_task
def clear_expired_sessions():
    call_command("clearsessions")
    logger.info("Виконано очищення прострочених сесій (clearsessions)")
