# Delivery Service — сервис международной доставки посылок

**Delivery Service** — REST API для регистрации посылок и расчёта стоимости их доставки. Пользователи регистрируются, создают посылки, получают список своих посылок с фильтрами и пагинацией. Встроен RAG-помощник службы поддержки на базе YandexGPT и ChromaDB.

## Возможности

- Регистрация и аутентификация (JWT + Google OAuth)
- Создание посылок и получение их списка с фильтрами (`parcel_type`, `calculated`)
- Получение детальной информации о посылке
- Справочник типов посылок (`clothes`, `electronics`, `other`)
- Периодический расчёт стоимости доставки (Celery beat, раз в 5 минут)
- RAG-помощник: ответы на вопросы по базе знаний правил доставки через YandexGPT + ChromaDB
- Логирование с `request_id` и разделением по компонентам (Loguru)
- Веб-интерфейс для управления посылками и общения с RAG-помощником

## Стек

| Компонент | Технологии |
| :--- | :--- |
| Язык | Python 3.12 |
| Бэкенд | Django 6.x, Django REST Framework, SimpleJWT, django-allauth |
| Периодические задачи | Celery 5.7, django-celery-beat |
| Кэш и брокер | Redis 7 |
| БД | PostgreSQL 16 |
| RAG | ChromaDB, YandexGPT (OpenAI-совместимый API) |
| Веб-сервер | Gunicorn + Nginx (в prod-профиле) |
| Контейнеризация | Docker, Docker Compose |
| Логирование | Loguru |
| Тестирование | pytest, pytest-django |
| Качество кода | ruff, mypy, radon, bandit, pre-commit |
| Пакетный менеджер | uv |
| Веб-интерфейс   | Vanilla JS (ES6+), HTML, CSS, Nginx (SPA + Reverse Proxy) |

## Быстрый старт (Docker Compose, рекомендуется)

### 1. Клонирование

```bash
git clone https://github.com/Lil4i4-lil/delivery_service
cd delivery_service
```

### 2. Переменные окружения

```bash
cp .env.example .env
```

Заполните `.env`:

```dotenv
APP_ENV=dev
DEBUG=True
SECRET_KEY=сгенерированный-ключ

# PostgreSQL — компоненты для сборки DATABASE_URL в compose
DATABASE_DB_PROD=delivery
DATABASE_USER_PROD=delivery
DATABASE_PASSWORD_PROD=ваш-пароль
DATABASE_HOST_PROD=db
DATABASE_PORT_PROD=5432

# Полная строка — для локального запуска без Docker
DATABASE_URL=postgres://delivery:ваш-пароль@localhost:5432/delivery

# YandexGPT
YANDEX_API_KEY=ваш-api-ключ
YANDEX_FOLDER_ID=ваш-folder-id
YANDEX_MODEL=yandexgpt-lite/latest
```

Сгенерировать `SECRET_KEY`:

```bash
uv run python scripts/get_key.py
```

### 3. Запуск

```bash
docker compose up --build
```

При первом запуске `entrypoint.sh` автоматически:
- ждёт готовности PostgreSQL,
- применяет миграции,
- создаёт три типа посылок и `PeriodicTask` для расчёта стоимости,
- загружает базу знаний в ChromaDB.

### 4. Суперпользователь

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Проверка

- API root: `http://localhost:8000/api/v1/`
- Swagger UI: **`http://localhost:8000/api/docs/`**
- Swagger schema (OpenAPI): `http://localhost:8000/api/schema/`
- Админка: `http://localhost:8000/admin/`

Остановка:

```bash
docker compose down
docker compose down -v
```

## API

| Метод | URL | Описание |
| :--- | :--- | :--- |
| `POST` | `/api/token/` | Получить JWT по `username` + `password` |
| `POST` | `/api/token/refresh/` | Обновить access-токен |
| `POST` | `/auth/accounts/google/login/` | Вход через Google (django-allauth) |
| `GET` | `/api/v1/parcel-type/` | Справочник типов посылок |
| `GET` | `/api/v1/parcels/` | Список своих посылок (пагинация, фильтры) |
| `POST` | `/api/v1/parcels/` | Создать посылку |
| `GET` | `/api/v1/parcels/{uuid}/` | Посылка по id |
| `POST` | `/api/v1/support/ask/` | RAG-вопрос службе поддержки |

Полная документация с возможностью отправлять запросы — **`/api/docs/`**. Нажмите **Authorize** и вставьте `access`-токен (без префикса `Bearer`).

## Веб-интерфейс (Frontend)

В проект встроен легковесный SPA-интерфейс, написанный на чистом JavaScript (без использования тяжелых фреймворков вроде React или Vue). 

**Возможности интерфейса:**
- Аутентификация по JWT (логин/пароль).
- Просмотр списка своих посылок.
- Создание новых посылок с выбором типа.
- Чат со службой поддержки (RAG-помощник на базе YandexGPT).

**Доступ:**
После запуска `docker compose up -d` интерфейс доступен по адресу **`http://localhost/`**.

## Локальная разработка

### 1. Окружение

```bash
uv sync
```

### 2. Инфраструктура

Postgres, Redis и ChromaDB удобнее поднять через compose:

```bash
docker compose up -d db redis chroma
```

### 3. Переменные окружения

В `.env` для локального запуска:

```dotenv
APP_ENV=dev
DATABASE_URL=postgres://delivery:ваш-пароль@localhost:5432/delivery
REDIS_URL=redis://localhost:6379/0
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

При `APP_ENV=dev` ChromaDB клиент подключается как `PersistentClient` к `delivery/chroma_data/` — отдельный контейнер `chroma` **не нужен**.

### 4. Миграции и данные

```bash
uv run manage.py migrate
uv run manage.py load_knowledge
uv run manage.py createsuperuser
```

### 5. Сервер

```bash
uv run manage.py runserver
```

## Celery (фоновые задачи)

Задачи запускаются автоматически через `beat` в Docker. Для локальной отладки:

```bash
# Worker (Windows: --pool=solo из-за особенностей billiard)
uv run celery -A delivery worker --pool=solo --loglevel=info

# Beat (DatabaseScheduler читает расписание из БД)
uv run celery -A delivery beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=info

# Обе команды одной строкой (только для разработки)
uv run celery -A delivery worker --beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --pool=solo --loglevel=info
```

Ручной запуск расчёта стоимости (вне расписания, синхронно, без worker):

```bash
# В Docker
docker compose exec web python manage.py calculate_delivery_costs

# Локально
uv run manage.py calculate_delivery_costs
```

## Тестирование

```bash
uv run pytest -v
```

Покрыты: модели, сериализаторы, CRUD-эндпоинты, фильтры, анти-IDOR (404 для чужих посылок), Celery-задача с моком курса ЦБ.

## Качество кода

```bash
make lint        # ruff check --fix
make fmt         # ruff format
make type        # mypy
make security    # bandit
make radon-check # radon: сложность и поддерживаемость
make check       # всё вместе (используется в pre-commit)
```

Pre-commit настроен на `make check` — при коммите автоматически прогоняются линтеры, типы, безопасность и метрики.

## Автор

**Михаил**

- GitHub: [@Lil4i4-lil](https://github.com/Lil4i4-lil)
- Email: mihanaz098@gmail.com