# shop/serializers.py
from rest_framework import serializers
from .models import Flower


class FlowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flower
        fields = ['id', 'name', 'price', 'description', 'image',]  # Выберите необходимые поля