# shop/views.py
from django.shortcuts import render, get_object_or_404
from .models import Flower
from django.shortcuts import render
from users.forms import UserRegisterForm

def flower_list(request):
    flowers = Flower.objects.all()
    return render(request, 'shop/flower_list.html', {'flowers': flowers})

def flower_detail(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    return render(request, 'shop/flower_detail.html', {'flower': flower})

def home(request):
    form = UserRegisterForm()
    return render(request, 'shop/index.html', {'form': form})