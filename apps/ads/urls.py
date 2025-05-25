from django.urls import path
from . import views

app_name = 'ads' # Оставляем это здесь для reverse lookup в веб-интерфейсе

urlpatterns = [
    # Объявления
    path('', views.AdListView.as_view(), name='ad_list'),
    path('create/', views.AdCreateView.as_view(), name='ad_create'),
    path('<int:pk>/', views.AdDetailView.as_view(), name='ad_detail'),
    path('<int:pk>/edit/', views.AdUpdateView.as_view(), name='ad_edit'),
    path('<int:pk>/delete/', views.AdDeleteView.as_view(), name='ad_delete'),
    path('my/', views.my_ads_view, name='my_ads'),

    # Предложения обмена
    path('proposals/', views.proposal_list_view, name='proposal_list'),
    path('proposals/create/<int:ad_id>/', views.create_proposal_view, name='proposal_create'),
    path('proposals/<int:pk>/accept/', views.accept_proposal_view, name='proposal_accept'),
    path('proposals/<int:pk>/reject/', views.reject_proposal_view, name='proposal_reject'),
]