from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва категорії")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL Slug")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ['name']

    def __str__(self):
        return self.name

class Book(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name = "Категорія"
    )
    title = models.CharField(max_length=200, verbose_name="Назва книги")
    author = models.CharField(max_length=150, verbose_name="Автор")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    description = models.TextField(blank=True, verbose_name="Опис")
    stock = models.PositiveIntegerField(default=0, verbose_name="Кількість в наявності")

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['title']

    def __str__(self):
        return self.title

class Tech(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва техніки")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Категорія")
    price = models.DecimalField(max_length=10, decimal_places=2, max_digits=10, verbose_name="Ціна")
    # додайте інші потрібні поля

    class Meta:
        verbose_name = "Техніка"
        verbose_name_plural = "Техніка"

    def __str__(self):
        return self.name