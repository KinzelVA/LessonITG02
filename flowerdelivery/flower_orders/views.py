# flower_orders/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    def get(self, request):
        username = request.GET.get('username')
        if not username:
            return Response({"error": "Username not provided"}, status=status.HTTP_400_BAD_REQUEST)

        orders = Order.objects.filter(user__username=username)
        if orders.exists():
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Orders not found"}, status=status.HTTP_404_NOT_FOUND)

