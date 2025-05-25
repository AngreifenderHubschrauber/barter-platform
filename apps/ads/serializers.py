from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']


class AdSerializer(serializers.ModelSerializer):
    """Сериализатор объявления"""
    user = UserSerializer(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    
    class Meta:
        model = Ad
        fields = [
            'id', 'user', 'title', 'description', 'image_url',
            'category', 'category_display', 'condition', 'condition_display',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        """Валидация заголовка"""
        if len(value) < 5:
            raise serializers.ValidationError('Заголовок должен содержать минимум 5 символов')
        return value
    
    def validate_description(self, value):
        """Валидация описания"""
        if len(value) < 20:
            raise serializers.ValidationError('Описание должно содержать минимум 20 символов')
        return value


class ExchangeProposalSerializer(serializers.ModelSerializer):
    """Сериализатор предложения обмена"""
    ad_sender = AdSerializer(read_only=True)
    ad_receiver = AdSerializer(read_only=True)
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Поля для создания предложения
    ad_sender_id = serializers.IntegerField(write_only=True)
    ad_receiver_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ExchangeProposal
        fields = [
            'id', 'ad_sender', 'ad_receiver', 'sender', 'receiver',
            'comment', 'status', 'status_display', 'created_at', 'updated_at',
            'ad_sender_id', 'ad_receiver_id'
        ]
        read_only_fields = ['id', 'sender', 'receiver', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Валидация предложения обмена"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Требуется авторизация')
        
        # Проверка существования объявлений
        try:
            ad_sender = Ad.objects.get(pk=data['ad_sender_id'])
            ad_receiver = Ad.objects.get(pk=data['ad_receiver_id'])
        except Ad.DoesNotExist:
            raise serializers.ValidationError('Одно из объявлений не найдено')
        
        # Проверка прав на отправку предложения
        if ad_sender.user != request.user:
            raise serializers.ValidationError('Вы можете предлагать обмен только своими товарами')
        
        if ad_receiver.user == request.user:
            raise serializers.ValidationError('Вы не можете предложить обмен сам себе')
        
        # Проверка активности объявлений
        if not ad_sender.is_active or not ad_receiver.is_active:
            raise serializers.ValidationError('Одно из объявлений неактивно')
        
        # Проверка на существующее предложение
        existing = ExchangeProposal.objects.filter(
            ad_sender=ad_sender,
            ad_receiver=ad_receiver
        ).exists()
        
        if existing:
            raise serializers.ValidationError('Предложение обмена уже существует')
        
        data['ad_sender'] = ad_sender
        data['ad_receiver'] = ad_receiver
        data['sender'] = request.user
        data['receiver'] = ad_receiver.user
        
        return data
    
    def create(self, validated_data):
        """Создание предложения обмена"""
        validated_data.pop('ad_sender_id', None)
        validated_data.pop('ad_receiver_id', None)
        return super().create(validated_data)


class ProposalStatusSerializer(serializers.Serializer):
    """Сериализатор для обновления статуса предложения"""
    status = serializers.ChoiceField(choices=['accepted', 'rejected'])
    
    def validate_status(self, value):
        """Валидация статуса"""
        proposal = self.context.get('proposal')
        request = self.context.get('request')
        
        if not proposal or not request:
            raise serializers.ValidationError('Недостаточно данных для валидации')
        
        # Проверка прав на изменение статуса
        if proposal.receiver != request.user:
            raise serializers.ValidationError('Только получатель может изменить статус предложения')
        
        if proposal.status != 'pending':
            raise serializers.ValidationError('Предложение уже обработано')
        
        return value