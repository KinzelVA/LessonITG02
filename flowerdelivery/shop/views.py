# shop/views.py
from django.shortcuts import render, get_object_or_404
from .models import Flower

def flower_list(request):
    flowers = Flower.objects.all()
    return render(request, 'shop/flower_list.html', {'flowers': flowers})

def flower_detail(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    return render(request, 'shop/flower_detail.html', {'flower': flower})

def home(request):
    """Главная страница сайта."""
    return render(request, 'shop/home.html')