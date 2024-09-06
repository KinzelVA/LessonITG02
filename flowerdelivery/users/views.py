from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserRegisterForm

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
