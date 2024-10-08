# Generated by Django 5.1.1 on 2024-09-19 19:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flower',
            fields=[
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image', models.URLField(blank=True, null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.TextField(default='Описание отсутствует')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='pending', max_length=20)),
                ('flower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.flower')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shop_orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
