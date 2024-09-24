# flowerdelivery\flower_orders\models.py
from django.db import models
from django.contrib.auth.models import User

class Flower(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Обрабатывается')

    def __str__(self):
        return f"Order {self.id} by {self.user.username} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # Связь с заказом
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)  # Связь с цветком
    quantity = models.PositiveIntegerField()  # Количество
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)  # Цена за штуку

    def __str__(self):
        return f"{self.quantity}x {self.flower.name} (Order {self.order.id})"
