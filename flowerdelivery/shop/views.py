# shop/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Flower
from users.forms import UserRegisterForm  # Форма регистрации
from rest_framework import viewsets
from .serializers import FlowerSerializer


class FlowerViewSet(viewsets.ModelViewSet):
    queryset = Flower.objects.all()
    serializer_class = FlowerSerializer
def flower_list(request):
    flowers = Flower.objects.all()
    return render(request, 'shop/flower_list.html', {'flowers': flowers})


def flower_detail(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    return render(request, 'shop/flower_detail.html', {'flower': flower})


def home(request):
    # Здесь больше нет формы регистрации
    return render(request, 'shop/home.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш аккаунт был создан!')
            return redirect('home')  # Возвращаемся на главную страницу после успешной регистрации
    else:
        form = UserRegisterForm()

    return render(request, 'shop/register.html', {'form': form})