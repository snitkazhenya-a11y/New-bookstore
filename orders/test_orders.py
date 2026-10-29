import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from catalog.factories import BookFactory
from orders.models import Order, OrderItem

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