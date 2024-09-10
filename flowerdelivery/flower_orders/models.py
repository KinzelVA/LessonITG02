from django.db import models
from django.conf import settings  # Для использования кастомной модели пользователя
from shop.models import Flower

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидается'),
        ('processing', 'В обработке'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')  # Используем кастомную модель пользователя
    flowers = models.ManyToManyField(Flower, related_name='orders')  # Поле для цветов, заказанных пользователем
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"
