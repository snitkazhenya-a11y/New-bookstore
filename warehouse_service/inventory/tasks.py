import logging
from celery import shared_task
from .models import StockItem

logger = logging.getLogger(__name__)


@shared_task
def check_low_stock(threshold: int = 3) -> list[int]:
    """Перевіряє товари із залишком меншим за поріг і логує попередження."""
    low_items = list(StockItem.objects.filter(quantity__lt=threshold).values_list("book_id", "quantity"))
    for book_id, quantity in low_items:
        logger.warning("Low stock alert: book_id=%s, quantity=%s (threshold=%s)", book_id, quantity, threshold)
    return [book_id for book_id, _ in low_items]