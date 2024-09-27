# flowerdelivery\flower_orders\models.py
from django.db import models
from django.contrib.auth.models import User



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Обрабатывается')
    order_details = models.TextField(null=True, blank=True)  # Добавляем поле для деталей заказа

    def __str__(self):
        return f"Order {self.id} by {self.user.username} ({self.status})"

