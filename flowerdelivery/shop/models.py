from django.db import models
from PIL import Image
import os
from django.contrib.auth import get_user_model

class Flower(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='flowers/', blank=True, null=True)  # Поле для загрузки изображения
    description = models.TextField(default="Описание отсутствует")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Сначала сохраняем изображение

        # Преобразуем изображение в JPG
        if self.image:
            img_path = self.image.path
            img = Image.open(img_path)
            if img.format != 'JPEG':
                # Заменяем формат изображения на JPEG
                jpg_image_path = os.path.splitext(img_path)[0] + ".jpg"
                img = img.convert('RGB')  # Преобразуем в RGB (JPEG не поддерживает альфа-канал)
                img.save(jpg_image_path, 'JPEG')

                # Обновляем поле изображения с новым путем
                self.image.name = os.path.basename(jpg_image_path)
                super().save(*args, **kwargs)  # Сохраняем снова с новым изображением

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'shop'  # Добавляем app_label, чтобы указать Django, к какому приложению относится модель

class Order(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='shop_orders')
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')  # Статус заказа

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} for {self.flower.name}"

    class Meta:
        app_label = 'shop'  # Добавляем app_label для модели Order
