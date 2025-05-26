from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import os


def ad_image_upload_path(instance, filename):
    """Путь для загрузки изображений объявлений"""
    # Получаем расширение файла
    ext = filename.split('.')[-1]
    # Создаем имя файла: ad_id_user_id.расширение
    filename = f'ad_{instance.user.id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.{ext}'
    return os.path.join('ads', filename)


class Ad(models.Model):
    """Модель объявления для обмена"""
    
    CATEGORY_CHOICES = [
        ('electronics', 'Электроника'),
        ('clothing', 'Одежда и обувь'),
        ('home', 'Дом и сад'),
        ('sports', 'Спорт и отдых'),
        ('books', 'Книги'),
        ('toys', 'Игрушки'),
        ('auto', 'Автотовары'),
        ('beauty', 'Красота и здоровье'),
        ('other', 'Другое'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('like_new', 'Почти новый'),
        ('good', 'Хорошее состояние'),
        ('fair', 'Удовлетворительное'),
    ]
    
    # id как автоинкрементное поле
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads', verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    # Добавляем поле для загрузки изображений
    image = models.ImageField(
        upload_to=ad_image_upload_path, 
        blank=True, 
        null=True, 
        verbose_name='Изображение',
        help_text='Загрузите изображение товара (максимум 5MB)'
    )
    image_url = models.URLField(blank=True, null=True, verbose_name='URL изображения')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, verbose_name='Состояние')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    
    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('ads:ad_detail', kwargs={'pk': self.pk})
    
    def get_image_url(self):
        """Получить URL изображения (приоритет: загруженное изображение, затем URL)"""
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None
    
    def can_edit(self, user):
        """Проверка прав на редактирование"""
        return self.user == user
    
    def can_delete(self, user):
        """Проверка прав на удаление"""
        return self.user == user
    
    def delete(self, *args, **kwargs):
        """Переопределяем удаление для удаления файла изображения"""
        if self.image:
            # Удаляем файл изображения при удалении объявления
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


class ExchangeProposal(models.Model):
    """Модель предложения обмена"""
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает рассмотрения'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]
    
    # id как автоинкрементное поле
    id = models.AutoField(primary_key=True)
    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='sent_proposals', verbose_name='Объявление отправителя')
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='received_proposals', verbose_name='Объявление получателя')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_proposals', verbose_name='Отправитель')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_proposals', verbose_name='Получатель')
    comment = models.TextField(verbose_name='Комментарий')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Предложение обмена'
        verbose_name_plural = 'Предложения обмена'
        ordering = ['-created_at']
        unique_together = ['ad_sender', 'ad_receiver']
    
    def __str__(self):
        return f'Обмен: {self.ad_sender.title} на {self.ad_receiver.title}'
    
    def can_accept(self, user):
        """Проверка прав на принятие предложения"""
        return self.receiver == user and self.status == 'pending'
    
    def can_reject(self, user):
        """Проверка прав на отклонение предложения"""
        return self.receiver == user and self.status == 'pending'
    
    def accept(self):
        """Принять предложение"""
        self.status = 'accepted'
        self.save()
        # Деактивировать объявления после успешного обмена
        self.ad_sender.is_active = False
        self.ad_sender.save()
        self.ad_receiver.is_active = False
        self.ad_receiver.save()
    
    def reject(self):
        """Отклонить предложение"""
        self.status = 'rejected'
        self.save()