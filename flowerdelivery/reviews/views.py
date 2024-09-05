# reviews/views.py

from django.shortcuts import render

# Страница отзывов
def review_list(request):
    return render(request, 'reviews/review_list.html')
