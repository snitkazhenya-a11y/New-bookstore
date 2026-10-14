import pytest
from catalog.factories import BookFactory
from cart.cart import Cart

# Generated with AI, reviewed and modified
@pytest.mark.django_db
def test_cart_add(client):
    book = BookFactory(price=100.00)

    session = client.session
    cart = Cart(request=type('obj', (object,), {'session': session})())

    cart.add(book=book, quantity=2)

    assert len(cart) == 2