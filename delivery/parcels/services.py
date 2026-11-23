from decimal import Decimal
import logging

from django.core.cache import cache
import requests

from delivery.constants import (
    CACHE_KEY,
    CACHE_TIMEOUT,
    CBR_URL,
    REQUEST_TIMEOUT,
)

logger = logging.getLogger(__name__)


def get_usd_rate() -> Decimal:
    """
    Возвращает курс доллара к рублю.
    Сначала пытается взять из кеша Redis, затем из API ЦБ.
    """
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return Decimal(str(cached))

    try:
        response = requests.get(CBR_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        rate = data['Valute']['USD']['Value']
        cache.set(CACHE_KEY, str(rate), CACHE_TIMEOUT)
        return Decimal(str(rate))
    except Exception as exc:
        logger.exception('Не удалось получить курс USD: %s', exc)
        fallback = cache.get(CACHE_KEY)
        if fallback is not None:
            return Decimal(str(fallback))
        raise
