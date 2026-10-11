import factory
from catalog.models import Book, Category

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f"Test Book {n}")
    description = factory.Faker("text")
    price = 299.99
    stock = 10
    category = factory.SubFactory(CategoryFactory)