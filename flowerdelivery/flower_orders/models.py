from django.db import models
from users.models import CustomUser
from shop.models import Flower

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидается'),
        ('processing', 'В обработке'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    flowers = models.ManyToManyField(Flower)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"

