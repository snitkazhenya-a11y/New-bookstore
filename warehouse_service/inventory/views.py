import logging
from django.core.cache import cache
from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import StockItem
from .serializers import StockItemSerializer

logger = logging.getLogger(__name__)
STOCK_LIST_CACHE_KEY = "warehouse_stock_list"


class IsWarehouseOperatorOrReadOnly(permissions.BasePermission):
    """Дозволяє читання автентифікованим, а зміну — персоналу або групі warehouse_managers."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff or request.user.is_superuser:
            return True
        return request.user.groups.filter(name="warehouse_managers").exists()


class BaseCachedModelViewSet(viewsets.ModelViewSet):
    """Базовий CBV із кешуванням списку та автоматичною інвалідацією."""

    cache_key = STOCK_LIST_CACHE_KEY
    cache_timeout = 300

    def invalidate_cache(self):
        cache.delete(self.cache_key)

    def list(self, request, *args, **kwargs):
        cached_data = cache.get(self.cache_key)
        if cached_data is not None:
            return Response(cached_data)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            cache.set(self.cache_key, response.data, timeout=self.cache_timeout)
            return response

        serializer = self.get_serializer(queryset, many=True)
        cache.set(self.cache_key, serializer.data, timeout=self.cache_timeout)
        return Response(serializer.data)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.invalidate_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.invalidate_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self.invalidate_cache()


class StockItemViewSet(BaseCachedModelViewSet):
    queryset = StockItem.objects.all().order_by("book_id")
    serializer_class = StockItemSerializer
    permission_classes = [IsWarehouseOperatorOrReadOnly]
    lookup_field = "book_id"

    @action(detail=True, methods=["post"])
    def reserve(self, request, book_id=None):
        try:
            amount = int(request.data.get("amount", 1))
        except (TypeError, ValueError):
            return Response(
                {"error": _("Параметр 'amount' має бути цілим числом.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if amount <= 0:
            return Response(
                {"error": _("Параметр 'amount' має бути більшим за 0.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            item = StockItem.objects.select_for_update().filter(book_id=book_id).first()
            if not item:
                return Response(
                    {"error": _("Товар з таким book_id не знайдено на складі.")},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if item.quantity < amount:
                return Response(
                    {"error": _("Недостатньо товару на складі"), "available": item.quantity},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            item.quantity -= amount
            item.save(update_fields=["quantity", "updated_at"])

        self.invalidate_cache()
        logger.info("Reserved %s units for book_id=%s; remaining=%s", amount, book_id, item.quantity)
        return Response({"status": "reserved", "remaining": item.quantity})