#user/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, data):
        # Проверка, что пароли совпадают
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Пароли должны совпадать."})

        # Проверка уникальности имени пользователя и email
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Пользователь с таким именем уже существует."})

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Пользователь с таким email уже существует."})

        return data

    def create(self, validated_data):
        # Удаляем поле password2, так как оно не требуется для создания пользователя
        validated_data.pop('password2')

        # Создаем нового пользователя
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )

        # Устанавливаем пароль
        user.set_password(validated_data['password'])
        user.save()

        return user
