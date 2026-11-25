# Delivery Service — Cервис доставки посылок

**Delivery Service** — это веб-сервис для отправки посылок. Пользователи могут регистрировать посылки, получать список своих посылок, получать детализированные данные о конкретной посылке.

## Основные возможности

- Регистрация и аутентификация пользователей
- Регистрация и получение информации о посылках
- Возможность задать вопрос службе поддержки
- Авторизация через сторонние сервисы (Google)

## Стек технологий

| Компонент       | Технологии                                 |
|-----------------|--------------------------------------------|
| Бэкенд          | Python 3.12, Django 6.0, DRF 3.18          |
| Периодические задачи | Celery 5.7                            |
| Кэширование     | Redis 8.10                                 |
| База данных     | PostgreSQL 18.6                            |
| Веб-сервер      | Gunicorn, Nginx                            |
| Контейнеризация | Docker, Docker Compose                     |
| Статика         | Nginx (отдача static файлов)               |
| CI/CD           | GitHub Actions                             |
| Тестирование    | pytest, pytest-django                      |
| Обвязка         | ruff, mypy, radon, bandit                  |


## Установка и запуск

### 1. Клонирование репозитория

```bash
  git clone https://github.com/ваш-username/delivery_service
  cd delivery_service
```

### 2. Настройка переменных окружения

Создайте файл .env на основе примера .env_example:    
```bash
  cp .env_example .env
```
Заполните .env своими значениями:
```
    APP_ENV=dev/prod
    DEBUG=True/False
    SECRET_KEY=сгенерированный-секретный-ключ
    
    DATABASE_DB_PROD=delivery
    DATABASE_USER_PROD=delivery
    DATABASE_PASSWORD_PROD=ваш-пароль
    DATABASE_HOST_PROD=db
    DATABASE_PORT_PROD=5432
    
    DATABASE_URL=URL-для-подключения-к-postgres
    
    YANDEX_API_KEY=api-ключ-для-отправки-запросов-к-yandexgpt
    YANDEX_FOLDER_ID=folder-id
    YANDEX_MODEL=llm-модель(yandexgpt-lite/latest)
```

Для генерации DJANGO_SECRET_KEY можно воспользоваться кодом из файла get_key.py

### 3. Запуск через Docker Compose (рекомендуется)

```bash
  docker compose up -d --build
```

Проект будет доступен по адресу http://localhost:8000.

Для остановки:
```bash
  docker compose down
```

### 4. Локальный запуск для разработки
Создайте и активируйте виртуальное окружение:
```bash
  python3 -m venv venv
  source venv/bin/activate  # Linux/Mac
  # или
  venv\Scripts\activate     # Windows
```

Установите зависимости:
```bash
  pip install -r requirements.txt
```

Запустите PostgreSQL (например, через Docker):
```bash
  docker compose up -d db
```

Примените миграции и запустите сервер:
```bash
  python manage.py migrate
  python manage.py runserver
```

### 5. Создание суперпользователя
```bash
  docker compose exec web python manage.py createsuperuser
```
Админ-панель: http://localhost:8000/admin/

## Автор
Михаил

* GitHub: https://github.com/Lil4i4-lil

* Email: mihanaz098@gmail.com

/api/docs - swagger-документация
Запуск celery worker: uv run celery -A delivery worker --pool=solo --loglevel=info
Запуск celery beat: uv run celery -A delivery beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=info                                                                          