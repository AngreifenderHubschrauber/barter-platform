from django.contrib import admin
from .models import Ad, ExchangeProposal


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """Админ-панель для объявлений"""
    list_display = ['title', 'user', 'category', 'condition', 'is_active', 'created_at']
    list_filter = ['category', 'condition', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    # Группировка полей
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title', 'description', 'image_url')
        }),
        ('Категоризация', {
            'fields': ('category', 'condition')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(ExchangeProposal)
class ExchangeProposalAdmin(admin.ModelAdmin):
    """Админ-панель для предложений обмена"""
    list_display = ['id', 'get_sender_ad', 'get_receiver_ad', 'sender', 'receiver', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['ad_sender__title', 'ad_receiver__title', 'sender__username', 'receiver__username']
    readonly_fields = ['created_at', 'updated_at']
    
    # Группировка полей
    fieldsets = (
        ('Объявления', {
            'fields': ('ad_sender', 'ad_receiver')
        }),
        ('Пользователи', {
            'fields': ('sender', 'receiver')
        }),
        ('Детали предложения', {
            'fields': ('comment', 'status')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_sender_ad(self, obj):
        """Отображение объявления отправителя"""
        return obj.ad_sender.title
    get_sender_ad.short_description = 'Объявление отправителя'
    
    def get_receiver_ad(self, obj):
        """Отображение объявления получателя"""
        return obj.ad_receiver.title
    get_receiver_ad.short_description = 'Объявление получателя'
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related('ad_sender', 'ad_receiver', 'sender', 'receiver')