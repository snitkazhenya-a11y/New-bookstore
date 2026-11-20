from unittest.mock import MagicMock, patch
import pytest
import requests
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from catalog.factories import BookFactory
from orders.models import Order, OrderItem
from orders.tasks import send_order_confirmation_email
from bookstore.services.warehouse_client import WarehouseServiceError, reserve_stock

User = get_user_model()


@pytest.mark.django_db
class TestOrderAPI:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='customer', password='password123')
        self.admin = User.objects.create_superuser(username='admin', password='adminpassword')
        self.book = BookFactory(price=250.00)
        self.order_list_url = reverse('order-list')

    def test_get_orders_authenticated(self):
        """Тест: авторизований користувач може переглядати список замовлень"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.order_list_url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_order_unauthenticated(self):
        """Тест: неавторизований користувач або гість створює замовлення"""
        data = {
            'name': 'Петро',
            'phone': '+380991234567',
            'city': 'Lviv',
            'zip_code': '79000',
            'email': 'petro@example.com',
            'address': 'St. 1'
        }
        response = self.client.post(self.order_list_url, data)
        # Залежно від вашої логіки дозволів (наприклад, дозволено гостям)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_create_order_invalid_data(self):
        """Тест: помилка валідації при створенні замовлення з порожніми полями"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.order_list_url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_can_access_all_orders(self):
        """Тест: адміністратор має доступ до керування замовленнями"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.order_list_url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_book_creation():
    order = Order.objects.create(
        name="Іван Франко",
        phone="+380501234567",
        city="Львів",
        zip_code="79000",
        email="ivan@example.com",
        address="вул. Коперника, 1"
    )

    book = BookFactory(price=200.00)
    OrderItem.objects.create(order=order, book=book, price=200.00, quantity=2)

    assert order.name == "Іван Франко"
    assert order.get_total_cost() == 400.00
    assert order.paid is False


@patch("bookstore.services.warehouse_client.requests.post")
def test_reserve_stock_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "reserved", "remaining": 8}
    mock_post.return_value = mock_resp

    result = reserve_stock(book_id=1, amount=2)

    assert result == {"status": "reserved", "remaining": 8}
    mock_post.assert_called_once()


@patch("bookstore.services.warehouse_client.sentry_sdk.capture_exception")
@patch("bookstore.services.warehouse_client.requests.post")
def test_reserve_stock_insufficient_stock(mock_post, mock_sentry):
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.json.return_value = {"error": "Недостатньо товару на складі"}
    mock_post.return_value = mock_resp

    with pytest.raises(WarehouseServiceError, match="Недостатньо товару на складі"):
        reserve_stock(book_id=1, amount=99)

    mock_sentry.assert_called_once()


@patch("bookstore.services.warehouse_client.sentry_sdk.capture_exception")
@patch("bookstore.services.warehouse_client.requests.post")
def test_reserve_stock_connection_error(mock_post, mock_sentry):
    mock_post.side_effect = requests.ConnectionError("Connection refused")

    with pytest.raises(WarehouseServiceError, match="Сервіс складу тимчасово недоступний"):
        reserve_stock(book_id=1, amount=1)

    mock_sentry.assert_called_once()


def test_reserve_stock_invalid_amount():
    with pytest.raises(WarehouseServiceError):
        reserve_stock(book_id=1, amount=0)


@patch("orders.tasks.send_mail")
def test_send_order_confirmation_email_task(mock_send_mail):
    send_order_confirmation_email.run(
        order_id=42,
        customer_name="Олег",
        customer_email="oleg@example.com",
    )

    mock_send_mail.assert_called_once()
    args, _ = mock_send_mail.call_args
    assert "42" in args[0]
    assert args[3] == ["oleg@example.com"]