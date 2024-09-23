# shop/models.py
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

        # Проверяем, есть ли изображение
        if self.image:
            img_path = self.image.path
            img = Image.open(img_path)

            # Уменьшаем изображение до ширины 250px, сохраняя пропорции
            max_size = (250, 250)
            img.thumbnail(max_size)

            # Если изображение не в формате JPEG, конвертируем его
            if img.format != 'JPEG':
                img = img.convert('RGB')  # Преобразуем в RGB, так как JPEG не поддерживает альфа-канал

                # Формируем новый путь для сохранения JPEG
                jpg_image_path = os.path.splitext(img_path)[0] + ".jpg"

                # Сохраняем изображение в формате JPEG
                img.save(jpg_image_path, 'JPEG', quality=85)

                # Обновляем путь к изображению в модели
                self.image.name = os.path.basename(jpg_image_path)

                # Удаляем оригинальный файл изображения
                if os.path.exists(img_path):
                    os.remove(img_path)

                # Снова сохраняем модель с обновленным путем к изображению
                super().save(*args, **kwargs)

            # Проверка и корректировка пути изображения
            correct_path = f"flowers/{os.path.basename(self.image.name)}"
            if self.image.name != correct_path:
                self.image.name = correct_path
                super().save(*args, **kwargs)  # Сохраняем модель еще раз с правильным путем

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'shop'


class Order(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='shop_orders')
    status = models.CharField(max_length=20, default='pending')  # Статус заказа

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    class Meta:
        app_label = 'shop'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # Связь с заказом
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)  # Связь с моделью Flower
    quantity = models.PositiveIntegerField()  # Количество
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)  # Цена за штуку

    def __str__(self):
        return f"{self.flower.name} x {self.quantity} (Order #{self.order.id})"

    class Meta:
        app_label = 'shop'
