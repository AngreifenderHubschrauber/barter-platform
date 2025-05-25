# API Documentation - Barter Platform

## Обзор

Barter Platform предоставляет RESTful API для работы с объявлениями и предложениями обмена. API использует стандартные HTTP методы и возвращает данные в формате JSON.

## Базовый URL

```
http://localhost:8000/api/
```

## Аутентификация

API использует сессионную аутентификацию Django. Для доступа к защищенным endpoints необходимо быть авторизованным пользователем.

### Вход в систему
```
POST /api-auth/login/
```

## Endpoints

### Объявления (Ads)

#### Получить список объявлений
```
GET /api/ads/
```

**Параметры запроса:**
- `page` - номер страницы
- `page_size` - количество элементов на странице
- `search` - поиск по заголовку и описанию
- `category` - фильтр по категории
- `condition` - фильтр по состоянию
- `ordering` - сортировка (created_at, -created_at)

**Пример ответа:**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/ads/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "username": "user1",
        "email": "user1@example.com"
      },
      "title": "iPhone 12 Pro",
      "description": "Отличный телефон в идеальном состоянии",
      "image_url": "https://example.com/image.jpg",
      "category": "electronics",
      "category_display": "Электроника",
      "condition": "like_new",
      "condition_display": "Почти новый",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z",
      "is_active": true
    }
  ]
}
```

#### Создать объявление
```
POST /api/ads/
```

**Тело запроса:**
```json
{
  "title": "Новое объявление",
  "description": "Описание товара",
  "image_url": "https://example.com/image.jpg",
  "category": "electronics",
  "condition": "new"
}
```

#### Получить объявление по ID
```
GET /api/ads/{id}/
```

#### Обновить объявление
```
PUT /api/ads/{id}/
PATCH /api/ads/{id}/
```

#### Удалить объявление
```
DELETE /api/ads/{id}/
```

#### Получить мои объявления
```
GET /api/ads/my_ads/
```

#### Деактивировать объявление
```
POST /api/ads/{id}/deactivate/
```

### Предложения обмена (Proposals)

#### Получить список предложений
```
GET /api/proposals/
```

**Параметры запроса:**
- `status` - фильтр по статусу (pending, accepted, rejected)
- `sender` - фильтр по отправителю
- `receiver` - фильтр по получателю

#### Создать предложение
```
POST /api/proposals/
```

**Тело запроса:**
```json
{
  "ad_sender_id": 1,
  "ad_receiver_id": 2,
  "comment": "Хочу обменяться!"
}
```

#### Получить предложение по ID
```
GET /api/proposals/{id}/
```

#### Принять предложение
```
POST /api/proposals/{id}/accept/
```

#### Отклонить предложение
```
POST /api/proposals/{id}/reject/
```

#### Получить отправленные предложения
```
GET /api/proposals/sent/
```

#### Получить полученные предложения
```
GET /api/proposals/received/
```

## Коды ошибок

- `200 OK` - Успешный запрос
- `201 Created` - Ресурс успешно создан
- `204 No Content` - Успешное удаление
- `400 Bad Request` - Неверный запрос
- `401 Unauthorized` - Требуется аутентификация
- `403 Forbidden` - Доступ запрещен
- `404 Not Found` - Ресурс не найден
- `500 Internal Server Error` - Ошибка сервера

## Примеры использования

### Python (requests)
```python
import requests

# Получить список объявлений
response = requests.get('http://localhost:8000/api/ads/')
ads = response.json()

# Создать объявление (требуется аутентификация)
session = requests.Session()
session.post('http://localhost:8000/api-auth/login/', {
    'username': 'user1',
    'password': 'password123'
})

new_ad = {
    'title': 'Новое объявление',
    'description': 'Описание',
    'category': 'electronics',
    'condition': 'new'
}
response = session.post('http://localhost:8000/api/ads/', json=new_ad)
```

### JavaScript (fetch)
```javascript
// Получить список объявлений
fetch('http://localhost:8000/api/ads/')
  .then(response => response.json())
  .then(data => console.log(data));

// Создать предложение обмена
fetch('http://localhost:8000/api/proposals/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  credentials: 'include',
  body: JSON.stringify({
    ad_sender_id: 1,
    ad_receiver_id: 2,
    comment: 'Хочу обменяться!'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Постраничная навигация

API использует постраничную навигацию для больших наборов данных:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/ads/?page=2",
  "previous": null,
  "results": [...]
}
```

- `count` - общее количество элементов
- `next` - URL следующей страницы
- `previous` - URL предыдущей страницы
- `results` - массив результатов текущей страницы

## Фильтрация и поиск

### Поиск по тексту
```
GET /api/ads/?search=iPhone
```

### Фильтрация по категории
```
GET /api/ads/?category=electronics
```

### Комбинированные фильтры
```
GET /api/ads/?category=electronics&condition=new&search=phone
```

### Сортировка
```
GET /api/ads/?ordering=-created_at  # Новые первыми
GET /api/ads/?ordering=created_at   # Старые первыми
```