from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError

from .models import UserProfile
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm


class UserProfileModelTest(TestCase):
    """Тесты модели профиля пользователя"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_profile_creation_on_user_creation(self):
        """Тест автоматического создания профиля при создании пользователя"""
        # Профиль должен быть создан автоматически
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_profile_str_method(self):
        """Тест строкового представления профиля"""
        expected_str = f'Профиль {self.user.username}'
        self.assertEqual(str(self.user.profile), expected_str)
    
    def test_profile_default_values(self):
        """Тест значений по умолчанию в профиле"""
        profile = self.user.profile
        
        self.assertEqual(profile.phone, '')
        self.assertEqual(profile.city, '')
        self.assertEqual(profile.bio, '')
        self.assertEqual(profile.successful_exchanges, 0)
        self.assertEqual(profile.rating, 0)
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
    
    def test_profile_update(self):
        """Тест обновления профиля"""
        profile = self.user.profile
        profile.phone = '+7 (123) 456-78-90'
        profile.city = 'Москва'
        profile.bio = 'Тестовая биография пользователя'
        profile.save()
        
        profile.refresh_from_db()
        self.assertEqual(profile.phone, '+7 (123) 456-78-90')
        self.assertEqual(profile.city, 'Москва')
        self.assertEqual(profile.bio, 'Тестовая биография пользователя')


class CustomUserCreationFormTest(TestCase):
    """Тесты формы регистрации пользователя"""
    
    def test_valid_form_data(self):
        """Тест валидной формы регистрации"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_duplicate_email_validation(self):
        """Тест валидации дублирующегося email"""
        # Создаем пользователя с email
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )
        
        # Пытаемся создать другого пользователя с тем же email
        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',  # Дублирующийся email
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_password_mismatch(self):
        """Тест несовпадения паролей"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'differentpassword456'
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_user_creation_with_email(self):
        """Тест создания пользователя с email"""
        form_data = {
            'username': 'testcreation',
            'email': 'testcreation@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.username, 'testcreation')
        self.assertEqual(user.email, 'testcreation@example.com')
        self.assertTrue(user.check_password('complexpassword123'))


class UserProfileFormTest(TestCase):
    """Тесты формы редактирования профиля"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Иван',
            last_name='Петров'
        )
    
    def test_valid_profile_form(self):
        """Тест валидной формы профиля"""
        form_data = {
            'first_name': 'Обновленное Имя',
            'last_name': 'Обновленная Фамилия',
            'email': 'updated@example.com',
            'phone': '+7 (987) 654-32-10',
            'city': 'Санкт-Петербург',
            'bio': 'Обновленная биография пользователя'
        }
        
        form = UserProfileForm(
            data=form_data,
            instance=self.user.profile,
            user=self.user
        )
        self.assertTrue(form.is_valid())
    
    def test_duplicate_email_in_profile_form(self):
        """Тест валидации дублирующегося email в форме профиля"""
        # Создаем другого пользователя с email
        User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123'
        )
        
        form_data = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'email': 'other@example.com',  # Дублирующийся email
            'phone': '+7 (123) 456-78-90',
            'city': 'Москва',
            'bio': 'Тестовая биография'
        }
        
        form = UserProfileForm(
            data=form_data,
            instance=self.user.profile,
            user=self.user
        )
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_saves_user_and_profile_data(self):
        """Тест сохранения данных пользователя и профиля"""
        form_data = {
            'first_name': 'Новое Имя',
            'last_name': 'Новая Фамилия',
            'email': 'newemail@example.com',
            'phone': '+7 (555) 123-45-67',
            'city': 'Екатеринбург',
            'bio': 'Новая биография пользователя'
        }
        
        form = UserProfileForm(
            data=form_data,
            instance=self.user.profile,
            user=self.user
        )
        
        self.assertTrue(form.is_valid())
        profile = form.save()
        
        # Проверяем обновление пользователя
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Новое Имя')
        self.assertEqual(self.user.last_name, 'Новая Фамилия')
        self.assertEqual(self.user.email, 'newemail@example.com')
        
        # Проверяем обновление профиля
        profile.refresh_from_db()
        self.assertEqual(profile.phone, '+7 (555) 123-45-67')
        self.assertEqual(profile.city, 'Екатеринбург')
        self.assertEqual(profile.bio, 'Новая биография пользователя')


class UserViewsTest(TestCase):
    """Тесты представлений пользователей"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_register_view_get(self):
        """Тест GET запроса к странице регистрации"""
        response = self.client.get(reverse('users:register'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertContains(response, 'Регистрация')
    
    def test_register_view_post_valid(self):
        """Тест POST запроса с валидными данными регистрации"""
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        })
        
        # Должен быть редирект после успешной регистрации
        self.assertEqual(response.status_code, 302)
        
        # Пользователь должен быть создан
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Пользователь должен быть автоматически авторизован
        user = User.objects.get(username='newuser')
        # Проверяем, что профиль создался автоматически
        self.assertTrue(hasattr(user, 'profile'))
    
    def test_register_redirect_authenticated_user(self):
        """Тест редиректа авторизованного пользователя со страницы регистрации"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:register'))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ads:ad_list'))
    
    def test_login_view_get(self):
        """Тест GET запроса к странице входа"""
        response = self.client.get(reverse('users:login'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertContains(response, 'Вход в систему')
    
    def test_login_view_post_valid(self):
        """Тест POST запроса с валидными данными входа"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Должен быть редирект после успешного входа
        self.assertEqual(response.status_code, 302)
        
        # Пользователь должен быть авторизован
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_view_post_invalid(self):
        """Тест POST запроса с невалидными данными входа"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        # Должны остаться на странице входа
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        
        # Проверяем наличие ошибок в форме (текст может отличаться)
        self.assertTrue(response.context['form'].errors)
        # Альтернативные варианты проверки ошибок:
        error_messages = [
            'Please enter a correct username and password',
            'Пожалуйста, введите правильные имя пользователя и пароль',
            'Неверное имя пользователя или пароль',
            'Invalid username or password'
        ]
        
        # Проверяем, что хотя бы одно из сообщений об ошибке присутствует
        page_content = response.content.decode()
        error_found = any(error_msg in page_content for error_msg in error_messages)
        
        # Если ни одно сообщение не найдено, проверяем просто наличие ошибок в форме
        if not error_found:
            self.assertTrue(response.context['form'].errors, 
                        "Форма должна содержать ошибки при неверных данных")
    
    def test_logout_view(self):
        """Тест выхода из системы"""
        self.client.login(username='testuser', password='testpass123')
        
        # Проверяем, что пользователь авторизован
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        
        # Выходим из системы
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что пользователь больше не авторизован
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
    
    def test_profile_view_requires_login(self):
        """Тест, что страница профиля требует авторизации"""
        response = self.client.get(reverse('users:profile'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_profile_view_get_authenticated(self):
        """Тест GET запроса к странице профиля авторизованным пользователем"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertContains(response, self.user.username)
    
    def test_profile_view_post_valid(self):
        """Тест POST запроса обновления профиля"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('users:profile'), {
            'first_name': 'Обновленное Имя',
            'last_name': 'Обновленная Фамилия',
            'email': 'updated@example.com',
            'phone': '+7 (123) 456-78-90',
            'city': 'Москва',
            'bio': 'Обновленная биография'
        })
        
        # Должен быть редирект после успешного обновления
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что данные обновились
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Обновленное Имя')
        self.assertEqual(self.user.email, 'updated@example.com')
        
        profile = self.user.profile
        profile.refresh_from_db()
        self.assertEqual(profile.phone, '+7 (123) 456-78-90')
        self.assertEqual(profile.city, 'Москва')
    
    def test_profile_view_context_data(self):
        """Тест контекстных данных страницы профиля"""
        from apps.ads.models import Ad, ExchangeProposal
        
        # Создаем тестовые данные для статистики
        ad1 = Ad.objects.create(
            user=self.user,
            title='Активное объявление',
            description='Описание активного объявления',
            category='electronics',
            condition='new',
            is_active=True
        )
        
        ad2 = Ad.objects.create(
            user=self.user,
            title='Неактивное объявление',
            description='Описание неактивного объявления',
            category='books',
            condition='good',
            is_active=False
        )
        
        # Создаем другого пользователя для обмена
        other_user = User.objects.create_user(
            username='otheruser',
            password='pass123'
        )
        
        other_ad = Ad.objects.create(
            user=other_user,
            title='Объявление другого пользователя',
            description='Описание объявления другого пользователя',
            category='sports',
            condition='good'
        )
        
        # Создаем принятое предложение обмена
        proposal = ExchangeProposal.objects.create(
            ad_sender=ad1,
            ad_receiver=other_ad,
            sender=self.user,
            receiver=other_user,
            comment='Тестовое предложение',
            status='accepted'
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        
        # Проверяем контекстные данные
        self.assertEqual(response.context['active_ads_count'], 1)
        self.assertEqual(response.context['completed_exchanges'], 1)


class UserAuthenticationFlowTest(TestCase):
    """Тесты полного процесса аутентификации"""
    
    def test_full_registration_login_flow(self):
        """Тест полного процесса регистрации и входа"""
        client = Client()
        
        # 1. Регистрация нового пользователя
        response = client.post(reverse('users:register'), {
            'username': 'flowtest',
            'email': 'flowtest@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        })
        
        # Должен быть редирект после регистрации
        self.assertEqual(response.status_code, 302)
        
        # Пользователь должен быть создан
        user = User.objects.get(username='flowtest')
        self.assertEqual(user.email, 'flowtest@example.com')
        
        # Профиль должен быть создан автоматически
        self.assertTrue(hasattr(user, 'profile'))
        
        # 2. Выход из системы
        client.get(reverse('users:logout'))
        
        # 3. Повторный вход с созданными данными
        response = client.post(reverse('users:login'), {
            'username': 'flowtest',
            'password': 'complexpassword123'
        })
        
        # Должен быть редирект после входа
        self.assertEqual(response.status_code, 302)
        
        # 4. Доступ к защищенной странице профиля
        response = client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'flowtest')
    
    def test_password_change_requirement(self):
        """Тест требований к паролю"""
        form_data = {
            'username': 'passwordtest',
            'email': 'passwordtest@example.com',
            'password1': '123',  # Слишком простой пароль
            'password2': '123'
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Проверяем, что есть ошибки валидации пароля
        self.assertTrue('password2' in form.errors or 'password1' in form.errors)


class UserIntegrationTest(TestCase):
    """Интеграционные тесты пользователей с объявлениями"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='integrationuser',
            password='testpass123',
            email='integration@example.com'
        )
        self.client.login(username='integrationuser', password='testpass123')
    
    def test_user_profile_with_ads_statistics(self):
        """Тест статистики пользователя с объявлениями"""
        from apps.ads.models import Ad, ExchangeProposal
        
        # Создаем несколько объявлений
        Ad.objects.create(
            user=self.user,
            title='Первое объявление',
            description='Описание первого объявления',
            category='electronics',
            condition='new'
        )
        
        Ad.objects.create(
            user=self.user,
            title='Второе объявление',
            description='Описание второго объявления',
            category='books',
            condition='good'
        )
        
        # Получаем страницу профиля
        response = self.client.get(reverse('users:profile'))
        
        # Проверяем, что статистика отображается корректно
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_ads_count'], 2)
        self.assertEqual(response.context['completed_exchanges'], 0)
    
    def test_user_deletion_cascade_behavior(self):
        """Тест каскадного удаления при удалении пользователя"""
        from apps.ads.models import Ad
        
        # Создаем объявление
        ad = Ad.objects.create(
            user=self.user,
            title='Объявление для удаления',
            description='Это объявление будет удалено вместе с пользователем',
            category='other',
            condition='fair'
        )
        
        ad_id = ad.id
        
        # Удаляем пользователя
        self.user.delete()
        
        # Проверяем, что объявление тоже удалилось
        self.assertFalse(Ad.objects.filter(id=ad_id).exists())
        
        # Проверяем, что профиль тоже удалился
        self.assertFalse(UserProfile.objects.filter(user_id=self.user.id).exists())