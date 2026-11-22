from .celery import app as celery_app
from .logging_setup import setup_logging

__all__ = ('celery_app',)

setup_logging()
