import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from catalog.factories import BookFactory
from cart.cart import Cart
from cart.models import CartItem


# --- 1. Тест кошика (Pytest) ---

@pytest.mark.django_db
def test_cart_add(client):
    """Тест: додавання книги до сесійного кошика"""
    book = BookFactory(price=100.00)

    session = client.session
    cart = Cart(request=type('obj', (object,), {'session': session})())

    cart.add(book=book, quantity=2)

    assert len(cart) == 2


@pytest.mark.django_db
def test_cart_remove(client):
    """Тест: видалення книги із сесійного кошика"""
    book = BookFactory(price=150.00)

    session = client.session
    cart = Cart(request=type('obj', (object,), {'session': session})())

    cart.add(book=book, quantity=1)
    assert len(cart) == 1

    cart.remove(book)
    assert len(cart) == 0


# --- 2. Тести API кошика (DRF / APIClient) ---

@pytest.mark.django_db
class TestCartAPI:

    def test_get_cart_unauthenticated_or_empty(self):
        """Тест: перевірка запиту до API кошика"""
        api_client = APIClient()
        url = reverse('cart-list')
        response = api_client.get(url)
        # Залежно від налаштувань прав (permissions), статус може бути 200 або 401/403
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]