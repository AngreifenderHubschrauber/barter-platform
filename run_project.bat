@echo off
REM Скрипт для быстрого запуска проекта на Windows

echo === Запуск Barter Platform ===

REM Проверка виртуального окружения
if not exist "venv" (
    echo Создание виртуального окружения...
    python -m venv venv
)

REM Активация виртуального окружения
echo Активация виртуального окружения...
call venv\Scripts\activate

REM Установка зависимостей
echo Установка зависимостей...
pip install -r requirements.txt

REM Создание .env файла если его нет
if not exist ".env" (
    echo Создание .env файла...
    copy .env.example .env
    echo Пожалуйста, отредактируйте .env файл и запустите скрипт снова
    pause
    exit /b 1
)

REM Применение миграций
echo Применение миграций...
python manage.py makemigrations
python manage.py migrate

REM Создание суперпользователя
echo Проверка суперпользователя...
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

REM Сбор статических файлов
echo Сбор статических файлов...
python manage.py collectstatic --noinput

REM Инициализация тестовых данных
set /p response="Хотите загрузить тестовые данные? (y/n): "
if /i "%response%"=="y" (
    python manage.py init_data
)

REM Запуск сервера разработки
echo Запуск сервера разработки...
echo ===================================
echo Сервер запущен на http://localhost:8000
echo Админ-панель: http://localhost:8000/admin
echo Логин: admin, Пароль: admin123
echo ===================================
python manage.py runserver