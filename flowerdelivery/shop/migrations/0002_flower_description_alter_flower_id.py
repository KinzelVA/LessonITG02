# Generated by Django 5.1.1 on 2024-09-10 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='flower',
            name='description',
            field=models.TextField(default='Описание отсутствует'),
        ),
        migrations.AlterField(
            model_name='flower',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
