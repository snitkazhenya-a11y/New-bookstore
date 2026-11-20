from django.apps import AppConfig
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from permissions import IsStoreManagerOrReadOnly

from .models import Book, Category
from .serializers import BookSerializer, CategorySerializer


class BaseCatalogViewSet(viewsets.ModelViewSet):
    """Базовий CBV для сутностей каталогу зі спільними правами доступу."""

    permission_classes = [IsStoreManagerOrReadOnly]


class CategoryViewSet(BaseCatalogViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BookViewSet(BaseCatalogViewSet):
    queryset = Book.objects.all().select_related("category")
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "price"]
    search_fields = ["title", "author"]
    ordering_fields = ["price", "created_at"]


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"

    def ready(self):
        import catalog.signals