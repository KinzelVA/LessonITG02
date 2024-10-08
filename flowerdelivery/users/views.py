# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserRegisterForm
from django.contrib.auth.forms import AuthenticationForm
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import UserRegisterSerializer
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

# API для регистрации
class UserRegisterAPIView(APIView):
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Пользователь успешно зарегистрирован!'}, status=status.HTTP_201_CREATED)
        else:
            # В случае ошибки добавим вывод в лог и отправим подробное сообщение
            print(serializer.errors)
            return Response({'errors': serializer.errors, 'message': 'Ошибка при регистрации'}, status=status.HTTP_400_BAD_REQUEST)

# Представление для формы регистрации
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            remember_me = request.POST.get('remember_me', False)
            login(request, user)

            # Устанавливаем время жизни сессии в зависимости от "Запомнить меня"
            if not remember_me:
                request.session.set_expiry(0)  # Сессия завершится при закрытии браузера
            else:
                request.session.set_expiry(1209600)  # Сессия сохранится на 2 недели

            username = form.cleaned_data.get('username')
            messages.success(request, f'Ваш аккаунт был создан, {username}!')
            return redirect('home')  # Перенаправляем на главную страницу после регистрации
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# Представление для входа в систему
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Перенаправление на главную страницу
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# API для получения пользователя по имени (username)
class UserByUsernameAPIView(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                return Response({'id': user.id, 'username': user.username}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Имя пользователя не указано'}, status=status.HTTP_400_BAD_REQUEST)
