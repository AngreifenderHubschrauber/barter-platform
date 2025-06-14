# Barter Platform

Монолитное веб-приложение на Django для организации обмена вещами между пользователями. Пользователи могут размещать объявления о товарах для обмена, просматривать чужие объявления и отправлять предложения на обмен.

## Функциональные возможности

### Основные функции
- Создание, редактирование и удаление объявлений
- Поиск и фильтрация объявлений по ключевым словам, категории и состоянию товара
- Пагинация результатов поиска
- Создание предложений обмена между пользователями
- Обновление статуса предложений (принятие/отклонение)
- Просмотр отправленных и полученных предложений
- Регистрация и авторизация пользователей
- Личный кабинет с профилем пользователя
- REST API для работы с объявлениями и предложениями

### Административные функции
- Админ-панель Django для управления контентом
- Система прав доступа (только автор может редактировать/удалять объявления)
- Автоматическая деактивация объявлений при успешном обмене

## Технический стек

- **Backend**: Python 3.8+, Django 4.2+
- **API**: Django REST Framework
- **База данных**: SQLite (разработка), PostgreSQL (продакшн)
- **Frontend**: Django Templates, Bootstrap 5
- **Тестирование**: Django TestCase, pytest
- **Дополнительные библиотеки**:
  - django-crispy-forms (формы)
  - django-cors-headers (CORS)
  - django-filter (фильтрация API)
  - Pillow (обработка изображений)

## Структура проекта

```
barter_platform/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── barter_platform/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── ads/                    # Приложение объявлений
│   │   ├── models.py          # Модели Ad, ExchangeProposal
│   │   ├── views.py           # Представления и API ViewSets
│   │   ├── forms.py           # Формы Django
│   │   ├── serializers.py     # DRF сериализаторы
│   │   ├── admin.py           # Админ-панель
│   │   ├── urls.py            # URL маршруты
│   │   ├── api_urls.py        # API маршруты
│   │   ├── tests.py           # Тесты
│   │   └── templates/ads/     # Шаблоны
│   └── users/                 # Приложение пользователей
│       ├── models.py          # Модель UserProfile
│       ├── views.py           # Представления пользователей
│       ├── forms.py           # Формы регистрации/профиля
│       ├── admin.py           # Админ-панель
│       ├── urls.py            # URL маршруты
│       ├── tests.py           # Тесты
│       └── templates/users/   # Шаблоны
├── templates/                 # Общие шаблоны
└── static/                   # Статические файлы
```

## Модели данных

### Ad (Объявление)
- `id` - автоинкрементное поле (Primary Key)
- `user` - связь с моделью User (автор объявления)
- `title` - заголовок объявления
- `description` - описание товара
- `image` - загруженное изображение товара
- `image_url` - URL внешнего изображения
- `category` - категория товара (выбор из списка)
- `condition` - состояние товара (выбор из списка)
- `created_at` - дата создания (автоматически)
- `updated_at` - дата обновления (автоматически)
- `is_active` - статус активности объявления

### ExchangeProposal (Предложение обмена)
- `id` - автоинкрементное поле (Primary Key)
- `ad_sender` - объявление отправителя
- `ad_receiver` - объявление получателя
- `sender` - пользователь-отправитель
- `receiver` - пользователь-получатель
- `comment` - комментарий к предложению
- `status` - статус предложения (ожидает/принято/отклонено)
- `created_at` - дата создания (автоматически)
- `updated_at` - дата обновления (автоматически)

## Установка и запуск

### Быстрый старт

#### Windows
```batch
run_project.bat
```

#### Linux/Mac
```bash
chmod +x run_project.sh
./run_project.sh
```

### Ручная установка

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd barter_platform
```

2. **Создание виртуального окружения**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

4. **Настройка переменных окружения**
```bash
cp .env.example .env
# Отредактировать .env файл при необходимости
```

5. **Применение миграций**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Создание суперпользователя**
```bash
python manage.py createsuperuser
```

7. **Загрузка тестовых данных (опционально)**
```bash
python manage.py init_data
```

8. **Запуск сервера разработки**
```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://localhost:8000

### Доступ к системе

- **Главная страница**: http://localhost:8000
- **Админ-панель**: http://localhost:8000/admin
- **API документация**: http://localhost:8000/api/

После загрузки тестовых данных доступны следующие аккаунты:
- Пользователи: user1-user5 (пароль: password123)
- Админ: admin (пароль: admin123) - создается автоматически скриптами

## API Endpoints

### Объявления
- `GET /api/ads/` - список всех объявлений
- `POST /api/ads/` - создание нового объявления (требует авторизации)
- `GET /api/ads/{id}/` - получение объявления по ID
- `PUT /api/ads/{id}/` - обновление объявления (только автор)
- `DELETE /api/ads/{id}/` - удаление объявления (только автор)
- `GET /api/ads/my_ads/` - мои объявления (требует авторизации)
- `POST /api/ads/{id}/deactivate/` - деактивация объявления (только автор)

### Предложения обмена
- `GET /api/proposals/` - список предложений (только участника)
- `POST /api/proposals/` - создание предложения (требует авторизации)
- `GET /api/proposals/{id}/` - получение предложения по ID
- `POST /api/proposals/{id}/accept/` - принятие предложения (только получатель)
- `POST /api/proposals/{id}/reject/` - отклонение предложения (только получатель)
- `GET /api/proposals/sent/` - отправленные предложения
- `GET /api/proposals/received/` - полученные предложения

### Параметры запросов API
- `page` - номер страницы
- `page_size` - количество элементов на странице
- `search` - поиск по заголовку и описанию
- `category` - фильтр по категории
- `condition` - фильтр по состоянию
- `ordering` - сортировка (created_at, -created_at)

## Тестирование

### Запуск всех тестов
```bash
python manage.py test
```

### Тесты по приложениям
```bash
python manage.py test apps.ads      # Тесты объявлений
python manage.py test apps.users    # Тесты пользователей
```

### Тесты с подробным выводом
```bash
python manage.py test --verbosity=2
```

### Анализ покрытия кода
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report --show-missing
coverage html
```

HTML отчет будет создан в директории `htmlcov/`

### Категории тестов
- **Модели**: тестирование бизнес-логики и валидации данных
- **Формы**: тестирование валидации форм пользователей
- **Представления**: тестирование HTTP-запросов и ответов
- **API**: тестирование REST API endpoints
- **Интеграционные тесты**: тестирование взаимодействия компонентов

## Развертывание

### Docker
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Продакшн настройки
1. Установить `DEBUG=False` в переменных окружения
2. Настроить PostgreSQL
3. Настроить статические файлы:
   ```bash
   python manage.py collectstatic
   ```
4. Использовать gunicorn или другой WSGI сервер
5. Настроить nginx для статических файлов

## Конфигурация

### Переменные окружения (.env)
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=barter_platform
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### Категории товаров
- electronics (Электроника)
- clothing (Одежда и обувь)
- home (Дом и сад)
- sports (Спорт и отдых)
- books (Книги)
- toys (Игрушки)
- auto (Автотовары)
- beauty (Красота и здоровье)
- other (Другое)

### Состояния товаров
- new (Новый)
- like_new (Почти новый)
- good (Хорошее состояние)
- fair (Удовлетворительное)

## Алгоритм работы системы

### Создание объявления
1. Пользователь заполняет форму с обязательными полями
2. Система генерирует уникальный ID и устанавливает дату создания
3. Объявление публикуется в активном состоянии
4. Добавляется в общий список для поиска

### Процесс обмена
1. Пользователь находит интересное объявление
2. Отправляет предложение обмена со своим товаром
3. Получатель рассматривает предложение
4. При принятии - оба объявления деактивируются
5. При отклонении - объявления остаются активными

### Поиск и фильтрация
1. Поиск по ключевым словам в заголовке и описании
2. Фильтрация по категории товара
3. Фильтрация по состоянию товара
4. Сортировка по дате создания
5. Пагинация результатов (12 объявлений на страницу)

## Права доступа

- **Неавторизованные пользователи**: просмотр объявлений
- **Авторизованные пользователи**: создание объявлений, отправка предложений
- **Автор объявления**: редактирование, удаление, деактивация
- **Получатель предложения**: принятие, отклонение предложений
- **Администраторы**: полный доступ через админ-панель

## Команды управления

### Инициализация тестовых данных
```bash
python manage.py init_data
```
Создает 5 тестовых пользователей и 10 объявлений с примерами предложений обмена.

### Сбор статических файлов
```bash
python manage.py collectstatic
```

### Создание миграций
```bash
python manage.py makemigrations
python manage.py migrate
```

## Техническая информация

### Требования к системе
- Python 3.8 или выше
- Django 4.2 или выше
- Поддержка SQLite/PostgreSQL
- Минимум 512MB RAM
- 1GB свободного места на диске

### Ограничения
- Максимальный размер загружаемого изображения: 5MB
- Минимальная длина заголовка: 5 символов
- Минимальная длина описания: 20 символов
- Один обмен между одной парой объявлений

### Безопасность
- CSRF защита включена
- Проверка прав доступа на уровне представлений
- Валидация данных на уровне форм и сериализаторов
- Защита от SQL-инъекций через Django ORM