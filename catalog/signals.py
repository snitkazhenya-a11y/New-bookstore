from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Book

@receiver([post_save, post_delete], sender=Book)
def invalidate_book_cache(sender, instance, **kwargs):
    # чистимо кеш певної книги та списку
    cache.delete(f"book_detail_{instance.pk}")
    cache.delete("book_list_cache")