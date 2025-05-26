# Barter Platform

Платформа для обмена вещами между пользователями. Пользователи могут размещать объявления о товарах для обмена, просматривать чужие объявления и отправлять предложения на обмен.

## Возможности

- Регистрация и авторизация пользователей
- Создание, редактирование и удаление объявлений
- Поиск и фильтрация объявлений по категориям и состоянию
- Отправка предложений на обмен
- Управление предложениями (принятие/отклонение)
- Личный кабинет с профилем пользователя
- REST API для работы с объявлениями и предложениями
- Админ-панель для управления контентом

## Технологии

- Python 3.8+
- Django 4.2+
- Django REST Framework
- SQLite (для разработки) / PostgreSQL (для продакшена)
- Bootstrap 5
- HTML/CSS/JavaScript

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd barter_platform
```

### 2. Создание виртуального окружения

```bash
python -m venv venv

# Активация виртуального окружения
# На Windows:
venv\Scripts\activate

# На Linux/Mac:
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Создайте файл `.env` в корневой директории проекта:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 7. Запуск сервера разработки

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://localhost:8000

## API Endpoints

### Объявления

- `GET /api/ads/` - Список всех объявлений
- `POST /api/ads/` - Создание нового объявления
- `GET /api/ads/{id}/` - Получение объявления по ID
- `PUT /api/ads/{id}/` - Обновление объявления
- `DELETE /api/ads/{id}/` - Удаление объявления
- `GET /api/ads/my_ads/` - Мои объявления
- `POST /api/ads/{id}/deactivate/` - Деактивация объявления

### Предложения обмена

- `GET /api/proposals/` - Список предложений
- `POST /api/proposals/` - Создание предложения
- `GET /api/proposals/{id}/` - Получение предложения
- `POST /api/proposals/{id}/accept/` - Принятие предложения
- `POST /api/proposals/{id}/reject/` - Отклонение предложения
- `GET /api/proposals/sent/` - Отправленные предложения
- `GET /api/proposals/received/` - Полученные предложения

## Тестирование

Запуск всех тестов:

```bash
python manage.py test
```

Запуск тестов конкретного приложения:

```bash
python manage.py test apps.ads
python manage.py test apps.users
```

## Деплой

Для деплоя в продакшн:

1. Установите `DEBUG=False` в настройках
2. Настройте PostgreSQL вместо SQLite
3. Настройте статические файлы:
   ```bash
   python manage.py collectstatic
   ```
4. Используйте gunicorn для запуска:
   ```bash
   gunicorn barter_platform.wsgi:application
   ```