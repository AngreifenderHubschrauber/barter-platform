from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Ad, ExchangeProposal


class AdModelTest(TestCase):
    """Тесты модели объявления"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_create_ad(self):
        """Тест создания объявления"""
        ad = Ad.objects.create(
            user=self.user,
            title='Тестовое объявление',
            description='Описание тестового объявления для проверки',
            category='electronics',
            condition='new'
        )
        
        self.assertEqual(ad.title, 'Тестовое объявление')
        self.assertEqual(ad.user, self.user)
        self.assertTrue(ad.is_active)
        self.assertIsNotNone(ad.created_at)
    
    def test_ad_str_method(self):
        """Тест строкового представления объявления"""
        ad = Ad.objects.create(
            user=self.user,
            title='Test Ad',
            description='Test description',
            category='books',
            condition='good'
        )
        
        self.assertEqual(str(ad), 'Test Ad')


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
            title='Test Ad',
            description='Test description for the ad',
            category='electronics',
            condition='new'
        )
    
    def test_ad_list_view(self):
        """Тест списка объявлений"""
        response = self.client.get(reverse('ads:ad_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ad')
        self.assertTemplateUsed(response, 'ads/ad_list.html')
    
    def test_ad_detail_view(self):
        """Тест детального просмотра объявления"""
        response = self.client.get(reverse('ads:ad_detail', kwargs={'pk': self.ad.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ad.title)
        self.assertContains(response, self.ad.description)
    
    def test_ad_create_requires_login(self):
        """Тест, что создание объявления требует авторизации"""
        response = self.client.get(reverse('ads:ad_create'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_ad_create_view(self):
        """Тест создания объявления авторизованным пользователем"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('ads:ad_create'), {
            'title': 'New Test Ad',
            'description': 'Description for the new test ad',
            'category': 'books',
            'condition': 'like_new'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(title='New Test Ad').exists())


class ExchangeProposalTest(TestCase):
    """Тесты предложений обмена"""
    
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
            title='Ad 1',
            description='Description 1',
            category='electronics',
            condition='new'
        )
        
        self.ad2 = Ad.objects.create(
            user=self.user2,
            title='Ad 2',
            description='Description 2',
            category='books',
            condition='good'
        )
    
    def test_create_proposal(self):
        """Тест создания предложения обмена"""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            sender=self.user1,
            receiver=self.user2,
            comment='Хочу обменяться!'
        )
        
        self.assertEqual(proposal.status, 'pending')
        self.assertEqual(proposal.sender, self.user1)
        self.assertEqual(proposal.receiver, self.user2)
    
    def test_accept_proposal(self):
        """Тест принятия предложения"""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            sender=self.user1,
            receiver=self.user2,
            comment='Test comment'
        )
        
        proposal.accept()
        
        self.assertEqual(proposal.status, 'accepted')
        self.assertFalse(self.ad1.is_active)
        self.assertFalse(self.ad2.is_active)
    
    def test_reject_proposal(self):
        """Тест отклонения предложения"""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            sender=self.user1,
            receiver=self.user2,
            comment='Test comment'
        )
        
        proposal.reject()
        
        self.assertEqual(proposal.status, 'rejected')
        self.assertTrue(self.ad1.is_active)
        self.assertTrue(self.ad2.is_active)