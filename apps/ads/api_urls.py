# apps/ads/urls_api.py
from django.urls import path
from . import views

app_name = 'api_ads'

urlpatterns = [
    # API Объявления
    path('ads/', views.AdListAPIView.as_view(), name='ad-list-create'),
    path('ads/search/', views.AdSearchAPIView.as_view(), name='ad-search'),
    path('ads/<int:pk>/', views.AdDetailAPIView.as_view(), name='ad-detail-update-delete'),

    # API Предложения обмена
    path('proposals/', views.ExchangeProposalListAPIView.as_view(), name='proposal-list-create'),
    path('proposals/<int:pk>/', views.ExchangeProposalDetailAPIView.as_view(), name='proposal-detail-update-delete'),
]