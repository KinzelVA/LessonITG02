# flower_orders/serializers.py
from rest_framework import serializers
from .models import Order
from shop.models import Flower
import logging

logger = logging.getLogger(__name__)

class FlowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flower
        fields = ['id', 'name']

class OrderSerializer(serializers.ModelSerializer):
    flowers = FlowerSerializer(many=True, read_only=True)
    flower_ids = serializers.PrimaryKeyRelatedField(queryset=Flower.objects.all(), many=True, write_only=True, source='flowers')
    address = serializers.CharField(allow_null=True, required=False)  # Адрес можно передавать пустым

    class Meta:
        model = Order
        fields = ['id', 'status', 'order_date', 'user', 'flowers', 'flower_ids', 'address']

    def create(self, validated_data):
        logger.info(f"Данные для создания заказа: {validated_data}")
        flower_ids = validated_data.pop('flowers')  # Извлечение цветов
        user = validated_data.pop('user')  # Извлечение пользователя
        order = Order.objects.create(user=user, **validated_data)
        order.flowers.set(flower_ids)  # Присваиваем цветы заказу
        return order
