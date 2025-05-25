# Руководство по развертыванию Barter Platform

## Развертывание на локальной машине

### Быстрый старт

#### Windows
```bash
run_project.bat
```

#### Linux/Mac
```bash
chmod +x run_project.sh
./run_project.sh
```

### Ручная установка

1. **Клонировать репозиторий**
```bash
git clone <repository-url>
cd barter_platform
```

2. **Создать виртуальное окружение**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Установить зависимости**
```bash
pip install -r requirements.txt
```

4. **Настроить переменные окружения**
```bash
cp .env.example .env
# Отредактировать .env файл
```

5. **Выполнить миграции**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Создать суперпользователя**
```bash
python manage.py createsuperuser
```

7. **Загрузить тестовые данные (опционально)**
```bash
python manage.py init_data
```

8. **Запустить сервер**
```bash
python manage.py runserver
```

## Развертывание с Docker

### Использование Docker Compose

1. **Запустить все сервисы**
```bash
docker-compose up -d
```

2. **Выполнить миграции**
```bash
docker-compose exec web python manage.py migrate
```

3. **Создать суперпользователя**
```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Загрузить тестовые данные**
```bash
docker-compose exec web python manage.py init_data
```

### Остановка сервисов
```bash
docker-compose down
```

## Развертывание на продакшн сервере

### Требования
- Ubuntu 20.04+ или другой Linux дистрибутив
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Supervisor или systemd

### Шаги развертывания

1. **Обновить систему**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Установить необходимые пакеты**
```bash
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx supervisor -y
```

3. **Создать пользователя для приложения**
```bash
sudo adduser barterapp
sudo usermod -aG www-data barterapp
```

4. **Настроить PostgreSQL**
```bash
sudo -u postgres psql
CREATE DATABASE barter_platform;
CREATE USER barteruser WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE barter_platform TO barteruser;
\q
```

5. **Клонировать проект**
```bash
sudo -u barterapp -H bash
cd /home/barterapp
git clone <repository-url>
cd barter_platform
```

6. **Создать виртуальное окружение**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

7. **Настроить переменные окружения**
```bash
cp .env.example .env
# Отредактировать .env с продакшн настройками
# Установить DEBUG=False
# Настроить SECRET_KEY
# Настроить DATABASE_URL
```

8. **Выполнить миграции и собрать статику**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

9. **Настроить Gunicorn**

Создать файл `/etc/supervisor/conf.d/barter_platform.conf`:
```ini
[program:barter_platform]
command=/home/barterapp/barter_platform/venv/bin/gunicorn --workers 3 --bind unix:/home/barterapp/barter_platform/barter_platform.sock barter_platform.wsgi:application
directory=/home/barterapp/barter_platform
user=barterapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/barterapp/logs/gunicorn.log
environment=PATH="/home/barterapp/barter_platform/venv/bin"
```

10. **Настроить Nginx**

Создать файл `/etc/nginx/sites-available/barter_platform`:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/barterapp/barter_platform;
    }
    
    location /media/ {
        root /home/barterapp/barter_platform;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/barterapp/barter_platform/barter_platform.sock;
    }
}
```

11. **Активировать конфигурацию**
```bash
sudo ln -s /etc/nginx/sites-available/barter_platform /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start barter_platform
```

## SSL сертификат (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

## Резервное копирование

### Создание резервной копии БД
```bash
pg_dump barter_platform > backup_$(date +%Y%m%d).sql
```

### Восстановление из резервной копии
```bash
psql barter_platform < backup_20240101.sql
```

## Мониторинг

### Логи приложения
```bash
tail -f /home/barterapp/logs/gunicorn.log
```

### Логи Nginx
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Статус сервисов
```bash
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status postgresql
```

## Обновление приложения

```bash
cd /home/barterapp/barter_platform
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart barter_platform
```

## Устранение неполадок

### Ошибка 502 Bad Gateway
- Проверить, запущен ли Gunicorn
- Проверить права на sock файл
- Проверить логи Gunicorn

### Ошибка 500 Internal Server Error
- Проверить настройки DEBUG=False
- Проверить ALLOWED_HOSTS
- Проверить подключение к БД
- Проверить логи приложения

### Статические файлы не загружаются
- Выполнить collectstatic
- Проверить настройки STATIC_ROOT
- Проверить конфигурацию Nginx