import pytest
from django.core.cache import cache
from catalog.models import Category, Book


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
def test_book_cache_invalidation_on_save():
    category = Category.objects.create(name="Fiction")
    book = Book.objects.create(
        title="Django for Professionals",
        slug="django-for-professionals",
        price=29.99,
        category=category
    )

    # Імітуємо збереження даних у кеш (low-level cache)
    cache_key = f"book_detail_{book.pk}"
    cache.set(cache_key, "cached_book_data")

    assert cache.get(cache_key) == "cached_book_data"

    # Оновлюємо книгу — сигнал має спрацювати і видалити кеш
    book.price = 34.99
    book.save()

    # Перевіряємо, що кеш інвалідовано (очищено)
    assert cache.get(cache_key) is None