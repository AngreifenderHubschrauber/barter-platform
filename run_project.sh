#!/bin/bash

# Скрипт для быстрого запуска проекта

echo "=== Запуск Barter Platform ==="

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "Установка зависимостей..."
pip install -r requirements.txt

# Создание .env файла если его нет
if [ ! -f ".env" ]; then
    echo "Создание .env файла..."
    cp .env.example .env
    echo "Пожалуйста, отредактируйте .env файл и запустите скрипт снова"
    exit 1
fi

# Применение миграций
echo "Применение миграций..."
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
echo "Проверка суперпользователя..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

# Сбор статических файлов
echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

# Инициализация тестовых данных
echo "Хотите загрузить тестовые данные? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py init_data
fi

# Запуск сервера разработки
echo "Запуск сервера разработки..."
echo "==================================="
echo "Сервер запущен на http://localhost:8000"
echo "Админ-панель: http://localhost:8000/admin"
echo "Логин: admin, Пароль: admin123"
echo "==================================="
python manage.py runserver