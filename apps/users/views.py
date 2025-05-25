from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import UserProfile


class RegisterView(CreateView):
    """Регистрация нового пользователя"""
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        # Сохраняем пользователя и автоматически входим в систему
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Добро пожаловать, {user.username}! Ваша учетная запись создана.')
        return redirect('ads:ad_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Перенаправление авторизованных пользователей
        if request.user.is_authenticated:
            return redirect('ads:ad_list')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    """Вход в систему"""
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        # Приветственное сообщение при входе
        response = super().form_valid(form)
        messages.success(self.request, f'Добро пожаловать, {self.request.user.username}!')
        return response


class CustomLogoutView(LogoutView):
    """Выход из системы"""
    next_page = 'ads:ad_list'
    
    def dispatch(self, request, *args, **kwargs):
        # Сообщение при выходе
        if request.user.is_authenticated:
            messages.info(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile_view(request):
    """Просмотр и редактирование профиля"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    # Получаем статистику пользователя
    from apps.ads.models import Ad, ExchangeProposal
    from django.db import models
    
    active_ads_count = Ad.objects.filter(user=request.user, is_active=True).count()
    completed_exchanges = ExchangeProposal.objects.filter(
        status='accepted'
    ).filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user)
    ).count()
    
    context = {
        'form': form,
        'profile': profile,
        'active_ads_count': active_ads_count,
        'completed_exchanges': completed_exchanges,
    }
    
    return render(request, 'users/profile.html', context)