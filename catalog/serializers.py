from rest_framework import serializers
from catalog.models import Book, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        extra_kwargs = {
            'slug': {'required': False}
        }


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'price',
            'description', 'category', 'category_id', 'created_at'
        ]

