# users/views.py
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')  # Убедитесь, что у вас есть URL с именем 'login'
    template_name = 'registration/signup.html'

def profile(request):
    return render(request, 'users/profile.html')
