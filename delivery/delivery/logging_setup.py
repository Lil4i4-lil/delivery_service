import os
import sys

from loguru import logger


def setup_logging():
    logger.remove()  # Убираем дефолтный sink

    # Консоль (для разработки) — все логи
    logger.add(sys.stdout, level="DEBUG",
               format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> | {message}")

    # Файл для посылок (parcels)
    logger.add(
        "logs/parcels.log",
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
        filter=lambda record: record["extra"].get("component") == "parcels",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message} | {extra}"
    )

    # Файл для службы поддержки (support)
    logger.add(
        "logs/support.log",
        level="DEBUG",  # В support полезно видеть DEBUG-логи (документы, промпты)
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
        filter=lambda record: record["extra"].get("component") == "support",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message} | {extra}"
    )

    # Файл для Celery (задачи)
    logger.add(
        "logs/celery.log",
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
        filter=lambda record: record["extra"].get("component") == "celery",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message} | {extra}"
    )

    # Общий файл для всего остального (на случай, если component не задан)
    logger.add(
        "logs/common.log",
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
        filter=lambda record: record["extra"].get("component") not in ("parcels", "support", "celery"),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
    )
