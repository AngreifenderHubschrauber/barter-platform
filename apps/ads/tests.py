import os
import tempfile
from decimal import Decimal
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from PIL import Image
import io

from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm, SearchForm


class AdModelTest(TestCase):
    """Тесты модели объявления"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
    def test_create_ad_with_minimal_data(self):
        """Тест создания объявления с минимальными данными"""
        ad = Ad.objects.create(
            user=self.user,
            title='Тестовое объявление',
            description='Описание тестового объявления для проверки функциональности системы',
            category='electronics',
            condition='new'
        )
        
        self.assertEqual(ad.title, 'Тестовое объявление')
        self.assertEqual(ad.user, self.user)
        self.assertEqual(ad.category, 'electronics')
        self.assertEqual(ad.condition, 'new')
        self.assertTrue(ad.is_active)
        self.assertIsNotNone(ad.created_at)
        self.assertIsNotNone(ad.updated_at)
    
    def test_create_ad_with_image_url(self):
        """Тест создания объявления с URL изображения"""
        ad = Ad.objects.create(
            user=self.user,
            title='Объявление с URL изображения',
            description='Тестовое описание объявления с внешним изображением',
            image_url='https://example.com/image.jpg',
            category='books',
            condition='good'
        )
        
        self.assertEqual(ad.image_url, 'https://example.com/image.jpg')
        self.assertEqual(ad.get_image_url(), 'https://example.com/image.jpg')
    
    def test_ad_str_method(self):
        """Тест строкового представления объявления"""
        ad = Ad.objects.create(
            user=self.user,
            title='Test Ad Title',
            description='Test description for the advertisement',
            category='books',
            condition='good'
        )
        
        self.assertEqual(str(ad), 'Test Ad Title')
    
    def test_ad_permissions(self):
        """Тест прав доступа к объявлению"""
        ad = Ad.objects.create(
            user=self.user,
            title='Permission Test Ad',
            description='Testing permissions for advertisement access',
            category='electronics',
            condition='new'
        )
        
        # Владелец может редактировать и удалять
        self.assertTrue(ad.can_edit(self.user))
        self.assertTrue(ad.can_delete(self.user))
        
        # Другой пользователь не может
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        self.assertFalse(ad.can_edit(other_user))
        self.assertFalse(ad.can_delete(other_user))
    
    def test_get_absolute_url(self):
        """Тест получения URL объявления"""
        ad = Ad.objects.create(
            user=self.user,
            title='URL Test Ad',
            description='Testing URL generation for advertisement',
            category='home',
            condition='like_new'
        )
        
        expected_url = reverse('ads:ad_detail', kwargs={'pk': ad.pk})
        self.assertEqual(ad.get_absolute_url(), expected_url)


class ExchangeProposalModelTest(TestCase):
    """Тесты модели предложения обмена"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )
        
        self.ad1 = Ad.objects.create(
            user=self.user1,
            title='iPhone для обмена',
            description='Отличный телефон в хорошем состоянии',
            category='electronics',
            condition='good'
        )
        
        self.ad2 = Ad.objects.create(
            user=self.user2,
            title='Книги по программированию',
            description='Коллекция книг по Python и Django',
            category='books',
            condition='like_new'
        )
    
    def test_create_proposal(self):
        """Тест создания предложения обмена"""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            sender=self.user1,
            receiver=self.user2,
            comment='Хочу обменять iPhone на ваши книги!'
        )
        
        self.assertEqual(proposal.status, 'pending')
        self.assertEqual(proposal.sender, self.user1)
        self.assertEqual(proposal.receiver, self.user2)
        self.assertEqual(proposal.ad_sender, self.ad1)
        self.assertEqual(proposal.ad_receiver, self.ad2)
        self.assertIsNotNone(proposal.created_at)
    
    def test_accept_proposal(self):
        """Тест принятия предложения"""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            sender=self.user1,
            receiver=self.user2,
            comment='Отличное предложение обмена'
        )
        
        # Проверяем, что получатель может принять
        self.assertTrue(proposal.can_accept(self.user2))
        self.assertFalse(proposal.can_accept(self.user1))
        
        # Принимаем предложение
        proposal.accept()
        
        # Проверяем результат
        self.assertEqual(proposal.status, 'accepted')
        
        # Проверяем, что объявления деактивированы
        self.ad1.refresh_from_db()
        self.ad2.refresh_from_db()
        self.assertFalse(self.ad1.is_active)
        self.assertFalse(self.ad2.is_active)
    
    def test_reject_proposal(self):
        """Тест отклонения предложения"""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            sender=self.user1,
            receiver=self.user2,
            comment='Предложение для отклонения'
        )
        
        # Проверяем, что получатель может отклонить
        self.assertTrue(proposal.can_reject(self.user2))
        self.assertFalse(proposal.can_reject(self.user1))
        
        # Отклоняем предложение
        proposal.reject()
        
        # Проверяем результат
        self.assertEqual(proposal.status, 'rejected')
        
        # Проверяем, что объявления остались активными
        self.ad1.refresh_from_db()
        self.ad2.refresh_from_db()
        self.assertTrue(self.ad1.is_active)
        self.assertTrue(self.ad2.is_active)
    
    def test_proposal_str_method(self):
        """Тест строкового представления предложения"""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            sender=self.user1,
            receiver=self.user2,
            comment='Тест строкового представления'
        )
        
        expected_str = f'Обмен: {self.ad1.title} на {self.ad2.title}'
        self.assertEqual(str(proposal), expected_str)
    
    def test_unique_together_constraint(self):
        """Тест ограничения уникальности пары объявлений"""
        # Создаем первое предложение
        ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            sender=self.user1,
            receiver=self.user2,
            comment='Первое предложение'
        )
        
        # Попытка создать дублирующее предложение должна вызвать ошибку
        with self.assertRaises(Exception):
            ExchangeProposal.objects.create(
                ad_sender=self.ad1,
                ad_receiver=self.ad2,
                sender=self.user1,
                receiver=self.user2,
                comment='Дублирующее предложение'
            )


class AdFormTest(TestCase):
    """Тесты формы объявления"""
    
    def test_valid_form_data(self):
        """Тест валидной формы"""
        form_data = {
            'title': 'Валидное тестовое объявление',
            'description': 'Это валидное описание объявления с достаточным количеством символов для прохождения валидации',
            'category': 'electronics',
            'condition': 'new',
            'image_url': 'https://example.com/image.jpg'
        }
        
        form = AdForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_short_title(self):
        """Тест невалидного короткого заголовка"""
        form_data = {
            'title': 'abc',  # Слишком короткий
            'description': 'Достаточно длинное описание для прохождения валидации формы',
            'category': 'electronics',
            'condition': 'new'
        }
        
        form = AdForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_invalid_short_description(self):
        """Тест невалидного короткого описания"""
        form_data = {
            'title': 'Валидный заголовок',
            'description': 'Короткое',  # Слишком короткое
            'category': 'books',
            'condition': 'good'
        }
        
        form = AdForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)


class AdViewsTest(TestCase):
    """Тесты представлений объявлений"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.ad = Ad.objects.create(
            user=self.user,
            title='Тестовое объявление для представлений',
            description='Описание тестового объявления для проверки представлений',
            category='electronics',
            condition='new'
        )
    
    def test_ad_list_view(self):
        """Тест списка объявлений"""
        response = self.client.get(reverse('ads:ad_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ad.title)
        self.assertTemplateUsed(response, 'ads/ad_list.html')
    
    def test_ad_detail_view(self):
        """Тест детального просмотра объявления"""
        response = self.client.get(reverse('ads:ad_detail', kwargs={'pk': self.ad.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ad.title)
        self.assertContains(response, self.ad.description)
        self.assertTemplateUsed(response, 'ads/ad_detail.html')
    
    def test_ad_create_requires_login(self):
        """Тест, что создание объявления требует авторизации"""
        response = self.client.get(reverse('ads:ad_create'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_ad_create_view_authenticated(self):
        """Тест создания объявления авторизованным пользователем"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('ads:ad_create'), {
            'title': 'Новое тестовое объявление',
            'description': 'Описание нового тестового объявления для проверки создания',
            'category': 'books',
            'condition': 'like_new'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(title='Новое тестовое объявление').exists())
    
    def test_ad_edit_permission(self):
        """Тест прав на редактирование объявления"""
        # Вход под владельцем
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ads:ad_edit', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Выход и вход под другим пользователем
        self.client.logout()
        other_user = User.objects.create_user(username='other', password='pass123')
        self.client.login(username='other', password='pass123')
        response = self.client.get(reverse('ads:ad_edit', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 403)
    
    def test_search_functionality(self):
        """Тест функциональности поиска"""
        # Создаем дополнительные объявления для поиска
        Ad.objects.create(
            user=self.user,
            title='Поиск по iPhone',
            description='Продам iPhone в отличном состоянии',
            category='electronics',
            condition='good'
        )
        
        # Поиск по заголовку
        response = self.client.get(reverse('ads:ad_list'), {'query': 'iPhone'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Поиск по iPhone')
        self.assertNotContains(response, 'Тестовое объявление для представлений')
        
        # Поиск по категории
        response = self.client.get(reverse('ads:ad_list'), {'category': 'electronics'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'electronics')


class ExchangeProposalViewsTest(TestCase):
    """Тесты представлений предложений обмена"""
    
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        
        self.ad1 = Ad.objects.create(
            user=self.user1,
            title='Объявление пользователя 1',
            description='Описание объявления первого пользователя',
            category='electronics',
            condition='new'
        )
        
        self.ad2 = Ad.objects.create(
            user=self.user2,
            title='Объявление пользователя 2',
            description='Описание объявления второго пользователя',
            category='books',
            condition='good'
        )
    
    def test_create_proposal_view(self):
        """Тест создания предложения обмена"""
        self.client.login(username='user1', password='pass123')
        
        response = self.client.post(
            reverse('ads:proposal_create', kwargs={'ad_id': self.ad2.pk}),
            {
                'ad_sender': self.ad1.pk,
                'comment': 'Хочу обменять мой товар на ваш!'
            }
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ExchangeProposal.objects.filter(
                ad_sender=self.ad1,
                ad_receiver=self.ad2
            ).exists()
        )
    
    def test_accept_proposal_view(self):
        """Тест принятия предложения"""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            sender=self.user1,
            receiver=self.user2,
            comment='Предложение для принятия'
        )
        
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('ads:proposal_accept', kwargs={'pk': proposal.pk}))
        
        self.assertEqual(response.status_code, 302)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'accepted')
    
    def test_reject_proposal_view(self):
        """Тест отклонения предложения"""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            sender=self.user1,
            receiver=self.user2,
            comment='Предложение для отклонения'
        )
        
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('ads:proposal_reject', kwargs={'pk': proposal.pk}))
        
        self.assertEqual(response.status_code, 302)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'rejected')


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ImageUploadTest(TestCase):
    """Тесты загрузки изображений"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def create_test_image(self):
        """Создание тестового изображения"""
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        return SimpleUploadedFile(
            name='test_image.jpg',
            content=image_file.getvalue(),
            content_type='image/jpeg'
        )
    
    def test_create_ad_with_uploaded_image(self):
        """Тест создания объявления с загруженным изображением"""
        test_image = self.create_test_image()
        
        response = self.client.post(reverse('ads:ad_create'), {
            'title': 'Объявление с изображением',
            'description': 'Тестовое объявление с загруженным изображением',
            'category': 'electronics',
            'condition': 'new',
            'image': test_image
        })
        
        self.assertEqual(response.status_code, 302)
        ad = Ad.objects.get(title='Объявление с изображением')
        self.assertTrue(ad.image)
        self.assertIsNotNone(ad.get_image_url())


class APITestCase(APITestCase):
    """Тесты REST API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123'
        )
        self.ad = Ad.objects.create(
            user=self.user,
            title='API тестовое объявление',
            description='Описание объявления для тестирования API',
            category='electronics',
            condition='new'
        )
    
    def test_get_ads_list_unauthorized(self):
        """Тест получения списка объявлений без авторизации"""
        url = '/api/ads/'  # Используем прямой URL
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_ad_requires_authentication(self):
        """Тест создания объявления через API требует авторизации"""
        url = '/api/ads/'  # Используем прямой URL
        data = {
            'title': 'API создание объявления',
            'description': 'Описание объявления созданного через API',
            'category': 'books',
            'condition': 'good'
        }
        
        response = self.client.post(url, data)
        # Django DRF может возвращать 403 вместо 401 в некоторых случаях
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_create_ad_authenticated(self):
        """Тест создания объявления через API с авторизацией"""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/ads/'  # Используем прямой URL
        data = {
            'title': 'API создание с авторизацией',
            'description': 'Описание объявления созданного авторизованным пользователем через API',
            'category': 'books',
            'condition': 'good'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data['title'])
    
    def test_update_ad_permission(self):
        """Тест обновления объявления через API с проверкой прав"""
        # Авторизация под владельцем
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/ads/{self.ad.pk}/'  # Используем прямой URL
        data = {
            'title': 'Обновленное название',
            'description': 'Обновленное описание объявления через API',
            'category': 'books',
            'condition': 'good'
        }
        
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], data['title'])
        
        # Попытка обновления другим пользователем
        other_user = User.objects.create_user(username='other', password='pass123')
        self.client.force_authenticate(user=other_user)
        
        response = self.client.put(url, data)
        # Может быть 403 или 404 в зависимости от настроек прав
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_api_search_and_filter(self):
        """Тест поиска и фильтрации через API"""
        # Создаем дополнительные объявления
        Ad.objects.create(
            user=self.user,
            title='Книги по Python',
            description='Коллекция книг по программированию на Python',
            category='books',
            condition='good'
        )
        
        # Поиск по заголовку
        url = '/api/ads/'  # Используем прямой URL
        response = self.client.get(url, {'search': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Фильтрация по категории
        response = self.client.get(url, {'category': 'books'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)