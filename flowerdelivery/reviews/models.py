from django.db import models
from users.models import CustomUser
from shop.models import Flower

class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField()

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.flower.name}"

