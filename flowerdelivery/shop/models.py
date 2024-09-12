from django.db import models
from django.contrib.auth import get_user_model

class Flower(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField(max_length=200, blank=True, null=True)
    id = models.AutoField(primary_key=True)
    description = models.TextField(default="Описание отсутствует")

    def __str__(self):
        return f"{self.name} - {self.price} руб."

class Order(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')  # Статус заказа

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} for {self.flower.name}"
