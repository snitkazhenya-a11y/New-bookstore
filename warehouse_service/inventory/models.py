from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class WarehouseUser(AbstractUser):
    """Кастомна модель користувача сервісу складу."""

    department = models.CharField(
        max_length=100,
        blank=True,
        default="main_warehouse",
        verbose_name=_("Відділ складу"),
    )

    class Meta:
        verbose_name = _("Користувач складу")
        verbose_name_plural = _("Користувачі складу")


class StockItem(models.Model):
    book_id = models.IntegerField(unique=True, verbose_name=_("ID книги в магазині"))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_("Кількість на складі"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Залишок товару")
        verbose_name_plural = _("Залишки товарів")

    def __str__(self):
        return f"Book ID {self.book_id}: {self.quantity} шт."