from rest_framework import serializers
from .models import StockItem

class StockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem
        fields = ['id', 'book_id', 'quantity', 'updated_at']