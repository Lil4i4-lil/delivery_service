import os
import logging

from celery import Celery
from celery.signals import setup_logging as celery_setup_logging
from loguru import logger

from delivery.logging_setup import setup_logging


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery.settings')

app = Celery('delivery')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.bind(component="celery").opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


@celery_setup_logging.connect
def config_loggers(*args, **kwargs):
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
