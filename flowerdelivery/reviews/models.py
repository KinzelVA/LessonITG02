from django.db import models
from django.contrib.auth.models import User
from shop.models import Flower
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # Рейтинг от 1 до 5
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания отзыва

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.flower.name} - {self.rating}/5"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
