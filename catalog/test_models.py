import pytest
from catalog.factories import BookFactory


@pytest.mark.django_db
def test_book_creation():
    # Створюємо тестову книгу
    book = BookFactory(title="Python Programming", price=450.00)

    # Перевіряємо, чи дані записалися правильно
    assert book.title == "Python Programming"
    assert float(book.price) == 450.00

@pytest.mark.django_db
def test_catalog_views(client):
    response = client.get('/')
    assert response.status_code in [200, 301, 302]