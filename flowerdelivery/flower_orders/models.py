# flowerdelivery\flower_orders\models.py
from django.db import models
from django.contrib.auth.models import User # Для использования кастомной модели пользователя
from shop.models import Flower

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    flowers = models.ManyToManyField(Flower, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=255, blank=True, null=True)  # Добавляем поле адреса
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"