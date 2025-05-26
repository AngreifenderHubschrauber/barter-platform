from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

# REST Framework imports
from rest_framework import generics, status, filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm, SearchForm
from .serializers import AdSerializer, ExchangeProposalSerializer, ProposalStatusSerializer
from .permissions import IsOwnerOrReadOnly


# ============= API VIEWS =============

class AdViewSet(viewsets.ModelViewSet):
    """API для работы с объявлениями"""
    queryset = Ad.objects.filter(is_active=True)
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
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
    
    def perform_update(self, serializer):
        """Обработка обновления с удалением старого изображения"""
        instance = self.get_object()
        # Если загружается новое изображение, удаляем старое
        if 'image' in self.request.FILES and instance.image:
            instance.image.delete(save=False)
        serializer.save()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_ads(self, request):
        """Получить объявления текущего пользователя"""
        ads = Ad.objects.filter(user=request.user)
        page = self.paginate_queryset(ads)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(ads, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def deactivate(self, request, pk=None):
        """Деактивировать объявление"""
        ad = self.get_object()
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
        return ExchangeProposal.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related('ad_sender', 'ad_receiver', 'sender', 'receiver')
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        """Принять предложение обмена"""
        proposal = self.get_object()
        
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
        page = self.paginate_queryset(proposals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(proposals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def received(self, request):
        """Получить полученные предложения"""
        proposals = self.get_queryset().filter(receiver=request.user)
        page = self.paginate_queryset(proposals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(proposals, many=True)
        return Response(serializer.data)


# ============= WEB VIEWS =============

class AdListView(ListView):
    """Список всех активных объявлений"""
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Ad.objects.filter(is_active=True).select_related('user')
        
        # Поиск и фильтрация
        form = SearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            category = form.cleaned_data.get('category')
            condition = form.cleaned_data.get('condition')
            
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) | Q(description__icontains=query)
                )
            if category:
                queryset = queryset.filter(category=category)
            if condition:
                queryset = queryset.filter(condition=condition)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm(self.request.GET)
        return context


class AdDetailView(DetailView):
    """Детальная страница объявления"""
    model = Ad
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            context['can_edit'] = self.object.can_edit(self.request.user)
            
            # Получаем активные объявления пользователя для предложения обмена
            context['user_ads'] = Ad.objects.filter(
                user=self.request.user,
                is_active=True
            ).exclude(pk=self.object.pk)
            
            # Другие объявления этого же пользователя
            context['other_ads_from_user'] = Ad.objects.filter(
                user=self.object.user,
                is_active=True
            ).exclude(pk=self.object.pk).order_by('?')[:5]

        return context


class AdCreateView(LoginRequiredMixin, CreateView):
    """Создание нового объявления"""
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Объявление успешно создано!')
        return super().form_valid(form)


class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование объявления"""
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    
    def test_func(self):
        return self.get_object().can_edit(self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Объявление успешно обновлено!')
        return super().form_valid(form)


class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление объявления"""
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('ads:my_ads')
    
    def test_func(self):
        return self.get_object().can_delete(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Объявление успешно удалено!')
        return super().delete(request, *args, **kwargs)


@login_required
def my_ads_view(request):
    """Мои объявления"""
    ads = Ad.objects.filter(user=request.user).order_by('-created_at')
    
    # Разделение на активные и неактивные
    active_ads = ads.filter(is_active=True)
    inactive_ads = ads.filter(is_active=False)
    
    context = {
        'active_ads': active_ads,
        'inactive_ads': inactive_ads,
    }
    return render(request, 'ads/my_ads.html', context)


@login_required
def create_proposal_view(request, ad_id):
    """Создание предложения обмена"""
    ad_receiver = get_object_or_404(Ad, pk=ad_id, is_active=True)
    
    # Проверка, что пользователь не может предложить обмен сам себе
    if ad_receiver.user == request.user:
        messages.error(request, 'Вы не можете предложить обмен на свое объявление!')
        return redirect('ads:ad_detail', pk=ad_id)
    
    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST, user=request.user)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_receiver = ad_receiver
            proposal.sender = request.user
            proposal.receiver = ad_receiver.user
            
            # Проверка на существующее предложение
            existing = ExchangeProposal.objects.filter(
                ad_sender=proposal.ad_sender,
                ad_receiver=proposal.ad_receiver
            ).first()
            
            if existing:
                messages.error(request, 'Вы уже отправляли предложение обмена на это объявление!')
                return redirect('ads:ad_detail', pk=ad_id)
            
            proposal.save()
            messages.success(request, 'Предложение обмена отправлено!')
            return redirect('ads:proposal_list')
    else:
        form = ExchangeProposalForm(user=request.user)
    
    context = {
        'form': form,
        'ad_receiver': ad_receiver,
    }
    return render(request, 'ads/proposal_form.html', context)


@login_required
def proposal_list_view(request):
    """Список предложений обмена"""
    sent_proposals = ExchangeProposal.objects.filter(
        sender=request.user
    ).select_related('ad_sender', 'ad_receiver', 'receiver')
    
    received_proposals = ExchangeProposal.objects.filter(
        receiver=request.user
    ).select_related('ad_sender', 'ad_receiver', 'sender')
    
    context = {
        'sent_proposals': sent_proposals,
        'received_proposals': received_proposals,
    }
    return render(request, 'ads/proposal_list.html', context)


@login_required
def accept_proposal_view(request, pk):
    """Принять предложение обмена"""
    proposal = get_object_or_404(ExchangeProposal, pk=pk)
    
    if not proposal.can_accept(request.user):
        messages.error(request, 'Вы не можете принять это предложение!')
        return redirect('ads:proposal_list')
    
    proposal.accept()
    messages.success(request, 'Предложение обмена принято! Объявления деактивированы.')
    return redirect('ads:proposal_list')


@login_required
def reject_proposal_view(request, pk):
    """Отклонить предложение обмена"""
    proposal = get_object_or_404(ExchangeProposal, pk=pk)
    
    if not proposal.can_reject(request.user):
        messages.error(request, 'Вы не можете отклонить это предложение!')
        return redirect('ads:proposal_list')
    
    proposal.reject()
    messages.success(request, 'Предложение обмена отклонено.')
    return redirect('ads:proposal_list')