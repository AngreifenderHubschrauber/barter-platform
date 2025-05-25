from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Ad, ExchangeProposal
from .serializers import AdSerializer, ExchangeProposalSerializer, ProposalStatusSerializer
from django.urls import path
from . import views


urlpatterns = [
    path('ads/', views.AdListAPIView.as_view(), name='list'),
    path('ads/<int:pk>/', views.AdDetailAPIView.as_view(), name='detail'),
    path('ads/search/', views.AdSearchAPIView.as_view(), name='search'),
    path('proposals/', views.ExchangeProposalListAPIView.as_view(), name='proposal-list'),
    path('proposals/<int:pk>/', views.ExchangeProposalDetailAPIView.as_view(), name='proposal-detail'),
]


class IsOwnerOrReadOnly(IsAuthenticated):
    """Разрешение: только владелец может редактировать/удалять"""
    
    def has_object_permission(self, request, view, obj):
        # НОВОЕ: Разрешить чтение всем
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # НОВОЕ: Разрешить изменение только владельцу
        return obj.user == request.user


class AdViewSet(viewsets.ModelViewSet):
    """API для работы с объявлениями"""
    queryset = Ad.objects.filter(is_active=True)
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'condition', 'user']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Определение прав доступа для разных действий"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrReadOnly()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Автоматическое присвоение пользователя при создании"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_ads(self, request):
        """Получить объявления текущего пользователя"""
        # НОВОЕ: Включить неактивные объявления для владельца
        ads = Ad.objects.filter(user=request.user)
        serializer = self.get_serializer(ads, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def deactivate(self, request, pk=None):
        """Деактивировать объявление"""
        ad = self.get_object()
        # НОВОЕ: Проверка прав
        if ad.user != request.user:
            return Response(
                {'error': 'Вы не можете деактивировать чужое объявление'},
                status=status.HTTP_403_FORBIDDEN
            )
        ad.is_active = False
        ad.save()
        return Response({'message': 'Объявление деактивировано'})


class ExchangeProposalViewSet(viewsets.ModelViewSet):
    """API для работы с предложениями обмена"""
    serializer_class = ExchangeProposalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'sender', 'receiver']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Получить предложения текущего пользователя"""
        user = self.request.user
        # НОВОЕ: Показывать только предложения, где пользователь участвует
        return ExchangeProposal.objects.filter(
            models.Q(sender=user) | models.Q(receiver=user)
        ).select_related('ad_sender', 'ad_receiver', 'sender', 'receiver')
    
    def create(self, request, *args, **kwargs):
        """Создание предложения обмена"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        """Принять предложение обмена"""
        proposal = self.get_object()
        
        # НОВОЕ: Использование сериализатора для валидации
        status_serializer = ProposalStatusSerializer(
            data={'status': 'accepted'},
            context={'proposal': proposal, 'request': request}
        )
        status_serializer.is_valid(raise_exception=True)
        
        proposal.accept()
        serializer = self.get_serializer(proposal)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """Отклонить предложение обмена"""
        proposal = self.get_object()
        
        # НОВОЕ: Использование сериализатора для валидации
        status_serializer = ProposalStatusSerializer(
            data={'status': 'rejected'},
            context={'proposal': proposal, 'request': request}
        )
        status_serializer.is_valid(raise_exception=True)
        
        proposal.reject()
        serializer = self.get_serializer(proposal)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Получить отправленные предложения"""
        proposals = self.get_queryset().filter(sender=request.user)
        serializer = self.get_serializer(proposals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def received(self, request):
        """Получить полученные предложения"""
        proposals = self.get_queryset().filter(receiver=request.user)
        serializer = self.get_serializer(proposals, many=True)
        return Response(serializer.data)