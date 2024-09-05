# analytics/views.py

from django.shortcuts import render

# Страница аналитики
def analytics_view(request):
    return render(request, 'analytics/analytics.html')
