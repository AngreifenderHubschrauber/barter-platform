from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm, SearchForm
from rest_framework import generics, permissions
from .serializers import AdSerializer, ExchangeProposalSerializer
from .permissions import IsOwnerOrReadOnly # Предполагается, что этот файл существует


# API Views
class AdListAPIView(generics.ListCreateAPIView):
    queryset = Ad.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AdDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsOwnerOrReadOnly]

class AdSearchAPIView(generics.ListAPIView):
    serializer_class = AdSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        category = self.request.query_params.get('category', '')
        condition = self.request.query_params.get('condition', '')
        queryset = Ad.objects.filter(is_active=True)
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if category:
            queryset = queryset.filter(category=category)
        if condition:
            queryset = queryset.filter(condition=condition)
        return queryset

class ExchangeProposalListAPIView(generics.ListCreateAPIView):
    queryset = ExchangeProposal.objects.all().order_by('-created_at')
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated] # Требует авторизации для предложений

    def get_queryset(self):
        # Пользователь может видеть только свои отправленные или полученные предложения
        return ExchangeProposal.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user)).order_by('-created_at')

    def perform_create(self, serializer):
        # Логика для автоматического определения sender и receiver
        ad_receiver_id = self.request.data.get('ad_receiver')
        ad_receiver_obj = Ad.objects.get(id=ad_receiver_id)
        serializer.save(sender=self.request.user, receiver=ad_receiver_obj.user)


class ExchangeProposalDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [IsOwnerOrReadOnly] # Или custom permission для предложений

    def get_queryset(self):
        # Пользователь может взаимодействовать только со своими предложениями
        return ExchangeProposal.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user))


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
        # Проверка, может ли пользователь редактировать объявление
        if self.request.user.is_authenticated:
            context['can_edit'] = self.object.can_edit(self.request.user)
            context['user_ads'] = Ad.objects.filter(
                user=self.request.user, 
                is_active=True
            ).exclude(pk=self.object.pk)
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
        # Проверка прав на редактирование
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
        # Проверка прав на удаление
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
    # Получаем отправленные и полученные предложения
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
    
    # Проверка прав на принятие предложения
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
    
    # Проверка прав на отклонение предложения
    if not proposal.can_reject(request.user):
        messages.error(request, 'Вы не можете отклонить это предложение!')
        return redirect('ads:proposal_list')
    
    proposal.reject()
    messages.success(request, 'Предложение обмена отклонено.')
    return redirect('ads:proposal_list')