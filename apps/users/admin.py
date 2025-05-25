from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Встроенная форма профиля пользователя"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    
    # Поля только для чтения
    readonly_fields = ['successful_exchanges', 'rating', 'created_at', 'updated_at']


class UserAdmin(BaseUserAdmin):
    """Расширенная админ-панель пользователей"""
    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']


# Перерегистрация модели User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Админ-панель для профилей пользователей"""
    list_display = ['user', 'phone', 'city', 'successful_exchanges', 'rating', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'city']
    readonly_fields = ['successful_exchanges', 'rating', 'created_at', 'updated_at']
    
    # Группировка полей
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Контактная информация', {
            'fields': ('phone', 'city')
        }),
        ('О пользователе', {
            'fields': ('bio',)
        }),
        ('Статистика', {
            'fields': ('successful_exchanges', 'rating'),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )