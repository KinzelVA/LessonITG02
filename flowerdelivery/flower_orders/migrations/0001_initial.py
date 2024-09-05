# Generated by Django 5.1.1 on 2024-09-05 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Ожидается'), ('processing', 'В обработке'), ('completed', 'Завершен'), ('canceled', 'Отменен')], default='pending', max_length=20)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('flowers', models.ManyToManyField(to='shop.flower')),
            ],
        ),
    ]
