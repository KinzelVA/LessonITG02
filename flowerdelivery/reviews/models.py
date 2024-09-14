from django.db import models
from django.contrib.auth.models import User
from shop.models import Flower

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField()

    def __str__(self):
        return f"Отзыв от {self.user} на {self.flower.name}"

