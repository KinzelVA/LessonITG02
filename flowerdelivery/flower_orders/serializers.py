from rest_framework import serializers
from .models import Order
from shop.models import Flower

class FlowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flower
        fields = ['id', 'name']  # Укажи только необходимые поля

class OrderSerializer(serializers.ModelSerializer):
    flowers = FlowerSerializer(many=True, read_only=True)  # Для отображения связанных цветов
    flower_ids = serializers.PrimaryKeyRelatedField(queryset=Flower.objects.all(), many=True, write_only=True, source='flowers')  # Для записи

    class Meta:
        model = Order
        fields = ['id', 'status', 'order_date', 'user', 'flowers', 'flower_ids']

    def create(self, validated_data):
        flower_ids = validated_data.pop('flowers')
        order = Order.objects.create(**validated_data)
        order.flowers.set(flower_ids)  # Установка ManyToMany поля
        return order
