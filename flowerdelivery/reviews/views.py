from rest_framework import viewsets
from .models import Review
from .serializers import ReviewSerializer
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

# Отключаем проверку CSRF для API ViewSet
@method_decorator(csrf_exempt, name='dispatch')
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  # Разрешаем доступ всем

    def create(self, request, *args, **kwargs):
        logger.info(f"Получен POST запрос: {request.data}")
        return super().create(request, *args, **kwargs)

# Функция для отображения списка отзывов на сайте
def review_list(request):
    reviews = Review.objects.all()
    return render(request, 'reviews/review_list.html', {'reviews': reviews})
