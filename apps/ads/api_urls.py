from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api_ads'

# Создаем роутер для ViewSets
router = DefaultRouter()
router.register(r'ads', views.AdViewSet, basename='ad')
router.register(r'proposals', views.ExchangeProposalViewSet, basename='proposal')

urlpatterns = [
    # Включаем все маршруты из роутера
    path('', include(router.urls)),
]