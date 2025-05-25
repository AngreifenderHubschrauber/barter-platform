from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.ads.models import Ad, ExchangeProposal
import random


class Command(BaseCommand):
    help = 'Инициализация тестовых данных для проекта'

    def handle(self, *args, **kwargs):
        self.stdout.write('Создание тестовых пользователей...')
        
        # НОВОЕ: Создание тестовых пользователей
        users = []
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                username=f'user{i}',
                defaults={
                    'email': f'user{i}@example.com',
                    'first_name': f'Пользователь',
                    'last_name': f'{i}',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                users.append(user)
                self.stdout.write(f'Создан пользователь: {user.username}')
            else:
                users.append(user)
                self.stdout.write(f'Пользователь уже существует: {user.username}')
        
        # НОВОЕ: Создание тестовых объявлений
        self.stdout.write('\nСоздание тестовых объявлений...')
        
        test_ads = [
            {
                'title': 'iPhone 12 Pro',
                'description': 'Отличный телефон в идеальном состоянии. Полный комплект, коробка, документы. Обменяю на ноутбук или планшет.',
                'category': 'electronics',
                'condition': 'like_new',
                'image_url': 'https://via.placeholder.com/400x300/007bff/ffffff?text=iPhone+12+Pro'
            },
            {
                'title': 'Велосипед горный Trek',
                'description': 'Профессиональный горный велосипед, 21 скорость, алюминиевая рама. Ищу электросамокат или спортивный инвентарь.',
                'category': 'sports',
                'condition': 'good',
                'image_url': 'https://via.placeholder.com/400x300/28a745/ffffff?text=Mountain+Bike'
            },
            {
                'title': 'Коллекция книг по программированию',
                'description': '15 книг по Python, JavaScript, алгоритмам. Все в отличном состоянии. Обменяю на электронную книгу или планшет.',
                'category': 'books',
                'condition': 'good',
                'image_url': 'https://via.placeholder.com/400x300/ffc107/000000?text=Programming+Books'
            },
            {
                'title': 'Кофемашина DeLonghi',
                'description': 'Автоматическая кофемашина, варит эспрессо, капучино. Обменяю на другую бытовую технику.',
                'category': 'home',
                'condition': 'like_new',
                'image_url': 'https://via.placeholder.com/400x300/6c757d/ffffff?text=Coffee+Machine'
            },
            {
                'title': 'PlayStation 4 Pro',
                'description': 'Игровая консоль с двумя джойстиками и 5 играми. Обменяю на Nintendo Switch или Xbox.',
                'category': 'electronics',
                'condition': 'good',
                'image_url': 'https://via.placeholder.com/400x300/dc3545/ffffff?text=PS4+Pro'
            },
            {
                'title': 'Гитара акустическая Yamaha',
                'description': 'Отличное звучание, мягкие струны, чехол в комплекте. Ищу электрогитару или синтезатор.',
                'category': 'other',
                'condition': 'good',
                'image_url': 'https://via.placeholder.com/400x300/17a2b8/ffffff?text=Acoustic+Guitar'
            },
            {
                'title': 'Набор для фитнеса',
                'description': 'Гантели, коврик, эспандеры, скакалка. Все новое. Обменяю на велотренажер или эллипсоид.',
                'category': 'sports',
                'condition': 'new',
                'image_url': 'https://via.placeholder.com/400x300/28a745/ffffff?text=Fitness+Set'
            },
            {
                'title': 'Куртка кожаная мужская',
                'description': 'Размер L, натуральная кожа, отличное состояние. Обменяю на другую одежду или обувь.',
                'category': 'clothing',
                'condition': 'like_new',
                'image_url': 'https://via.placeholder.com/400x300/343a40/ffffff?text=Leather+Jacket'
            },
            {
                'title': 'Lego Technic набор',
                'description': 'Большой набор 2000+ деталей, все инструкции. Обменяю на другие конструкторы или настольные игры.',
                'category': 'toys',
                'condition': 'good',
                'image_url': 'https://via.placeholder.com/400x300/ffc107/000000?text=Lego+Technic'
            },
            {
                'title': 'Фотоаппарат Canon EOS',
                'description': 'Зеркальная камера с объективом 18-55mm. Ищу видеокамеру или дрон.',
                'category': 'electronics',
                'condition': 'good',
                'image_url': 'https://via.placeholder.com/400x300/6c757d/ffffff?text=Canon+Camera'
            }
        ]
        
        created_ads = []
        for i, ad_data in enumerate(test_ads):
            user = users[i % len(users)]
            ad, created = Ad.objects.get_or_create(
                title=ad_data['title'],
                user=user,
                defaults=ad_data
            )
            if created:
                created_ads.append(ad)
                self.stdout.write(f'Создано объявление: {ad.title}')
            else:
                self.stdout.write(f'Объявление уже существует: {ad.title}')
        
        # НОВОЕ: Создание тестовых предложений обмена
        if len(created_ads) >= 4:
            self.stdout.write('\nСоздание тестовых предложений обмена...')
            
            # Создаем несколько предложений
            proposals_data = [
                {
                    'ad_sender': created_ads[0],
                    'ad_receiver': created_ads[1],
                    'comment': 'Отличное предложение! Давно искал такой велосипед.',
                    'status': 'pending'
                },
                {
                    'ad_sender': created_ads[2],
                    'ad_receiver': created_ads[3],
                    'comment': 'Готов обменять книги на вашу кофемашину.',
                    'status': 'pending'
                },
                {
                    'ad_sender': created_ads[4],
                    'ad_receiver': created_ads[5],
                    'comment': 'PlayStation на гитару - отличный обмен!',
                    'status': 'accepted'
                }
            ]
            
            for prop_data in proposals_data:
                proposal, created = ExchangeProposal.objects.get_or_create(
                    ad_sender=prop_data['ad_sender'],
                    ad_receiver=prop_data['ad_receiver'],
                    defaults={
                        'sender': prop_data['ad_sender'].user,
                        'receiver': prop_data['ad_receiver'].user,
                        'comment': prop_data['comment'],
                        'status': prop_data['status']
                    }
                )
                if created:
                    self.stdout.write(f'Создано предложение обмена: {proposal}')
        
        self.stdout.write(self.style.SUCCESS('\nИнициализация данных завершена!'))
        self.stdout.write('\nТестовые пользователи:')
        for i in range(1, 6):
            self.stdout.write(f'  Логин: user{i}, Пароль: password123')