# delivery_service
/api/docs - swagger-документация
Запуск celery worker: uv run celery -A delivery worker --pool=solo --loglevel=info
Запуск celery beat: uv run celery -A delivery beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=info                                                                          