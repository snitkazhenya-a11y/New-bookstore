import pytest
from orders.models import Order, OrderItem
from catalog.factories import BookFactory


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