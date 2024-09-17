# flowerdelivery\flower_orders\models.py
from django.db import models
from django.contrib.auth.models import User  # Для использования модели пользователя Django
from shop.models import Flower

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    flowers = models.ManyToManyField(Flower, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=255, blank=True, null=True)  # Поле адреса может быть пустым
    status = models.CharField(max_length=20, default='pending')  # Статус заказа

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"
