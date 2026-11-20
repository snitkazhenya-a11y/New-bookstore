import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from rest_framework.test import APIClient

from inventory.models import StockItem
from inventory.tasks import check_low_stock

User = get_user_model()


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


def get_auth_client(with_manager_group=True):
    user = User.objects.create_user(
        username="warehouse_client",
        password="password123",
        department="logistics",
    )
    if with_manager_group:
        group, _ = Group.objects.get_or_create(name="warehouse_managers")
        user.groups.add(group)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_stock_list_cache_and_reserve():
    """Список кешується, а резервування зменшує залишок і чистить кеш."""
    item = StockItem.objects.create(book_id=10, quantity=5)
    client = get_auth_client()

    list_resp = client.get("/api/warehouse/stock/")
    assert list_resp.status_code == 200
    assert cache.get("warehouse_stock_list") is not None

    res_resp = client.post("/api/warehouse/stock/10/reserve/", {"amount": 2}, format="json")
    assert res_resp.status_code == 200
    assert res_resp.data["remaining"] == 3
    assert cache.get("warehouse_stock_list") is None

    item.refresh_from_db()
    assert item.quantity == 3


@pytest.mark.django_db
def test_stock_reserve_not_enough_quantity():
    """Відмова у резервуванні (400), якщо на складі менше товару, ніж запрошено."""
    StockItem.objects.create(book_id=11, quantity=1)
    client = get_auth_client()

    resp = client.post("/api/warehouse/stock/11/reserve/", {"amount": 5}, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_stock_reserve_invalid_amount():
    """Відмова у резервуванні (400) при некоректному amount."""
    StockItem.objects.create(book_id=12, quantity=5)
    client = get_auth_client()

    resp_zero = client.post("/api/warehouse/stock/12/reserve/", {"amount": 0}, format="json")
    assert resp_zero.status_code == 400

    resp_nan = client.post("/api/warehouse/stock/12/reserve/", {"amount": "abc"}, format="json")
    assert resp_nan.status_code == 400


@pytest.mark.django_db
def test_stock_reserve_not_found():
    """Повернення 404, якщо запис з book_id відсутній на складі."""
    client = get_auth_client()

    resp = client.post("/api/warehouse/stock/9999/reserve/", {"amount": 1}, format="json")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_permission_denied_without_group_and_language_header():
    """Користувач без групи warehouse_managers не може змінювати залишки, а мова враховується."""
    StockItem.objects.create(book_id=15, quantity=4)
    client = get_auth_client(with_manager_group=False)

    resp = client.post(
        "/api/warehouse/stock/15/reserve/",
        {"amount": 1},
        format="json",
        HTTP_ACCEPT_LANGUAGE="en",
    )
    assert resp.status_code == 403


@pytest.mark.django_db
def test_check_low_stock_task():
    """Celery-задача повертає список book_id із низьким залишком."""
    StockItem.objects.create(book_id=20, quantity=1)
    StockItem.objects.create(book_id=21, quantity=10)

    low_ids = check_low_stock(threshold=3)
    assert low_ids == [20]