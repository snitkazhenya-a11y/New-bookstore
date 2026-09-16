from django.db import models
from django.conf import settings

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Текст поста")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення поста")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор")

    def __str__(self):
        return self.title
