from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created')
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Order.objects.all().order_by('-created')

    def perform_create(self, serializer):
        serializer.save()