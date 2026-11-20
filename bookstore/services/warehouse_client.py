import logging
import os
import requests
import sentry_sdk

logger = logging.getLogger(__name__)

WAREHOUSE_API_URL = os.environ.get("WAREHOUSE_API_URL", "http://web_b:8001").rstrip("/")
WAREHOUSE_STOCK_PATH = os.environ.get(
    "WAREHOUSE_STOCK_PATH", "/api/warehouse/stock"
).strip("/")
TIMEOUT_SECONDS = 5


class WarehouseServiceError(Exception):
    """Помилка комунікації або резервування товару на складі."""


def reserve_stock(book_id: int | str, amount: int = 1) -> dict:
    if amount <= 0:
        raise WarehouseServiceError("Кількість для резервування має бути більшою за 0.")

    url = f"{WAREHOUSE_API_URL}/{WAREHOUSE_STOCK_PATH}/{book_id}/reserve/"
    payload = {"amount": amount}

    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        sentry_sdk.capture_exception(exc)
        logger.error("Не вдалося з'єднатися зі складом (%s): %s", url, exc)
        raise WarehouseServiceError("Сервіс складу тимчасово недоступний.") from exc

    if response.status_code == 200:
        return response.json()

    try:
        error_data = response.json()
    except ValueError:
        error_data = {"error": response.text}

    message = (
        error_data.get("error")
        or error_data.get("detail")
        or "Помилка резервування на складі."
    )
    err = WarehouseServiceError(message)
    sentry_sdk.capture_exception(err)

    logger.warning(
        "Склад відхилив резервування book_id=%s, amount=%s (HTTP %s): %s",
        book_id,
        amount,
        response.status_code,
        message,
    )
    raise WarehouseServiceError(message)
