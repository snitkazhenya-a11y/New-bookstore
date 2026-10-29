from rest_framework import serializers
from catalog.serializers import BookSerializer
from catalog.models import Book
from orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'book_id', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='item')  # або 'items' залежно від related_name

    class Meta:
        model = Order
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'city',
            'zip_code', 'paid', 'created', 'updated', 'items'
        ]
        read_only_fields = ['created', 'updated']