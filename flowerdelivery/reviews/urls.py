# reviews/urls.py
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = router.urls

