from decimal import Decimal

from celery import shared_task
from loguru import logger

from .models import Parcel
from .services import get_usd_rate
from delivery.constants import (
    TASK_MAX_RETRIES,
    TASK_DEFAULT_RETRY_DELAY,
    FORMULA_WEIGHT_COEFFICIENT,
    FORMULA_COST_COEFFICIENT,
)


@shared_task(
    bind=True,
    max_retries=TASK_MAX_RETRIES,
    default_retry_delay=TASK_DEFAULT_RETRY_DELAY
)
def calculate_delivery_costs(self):
    """
    Рассчитывает стоимость доставки для всех посылок,
    у которых delivery_cost = NULL.
    """
    task_logger = logger.bind(component="celery", task_id=self.request.id, task_name=self.name)
    task_logger.info("Начало вычисления стоимости доставки")

    try:
        usd_rate = get_usd_rate()
    except Exception as exc:
        task_logger.error("Не удалось получить курс USD: {exc}", exc=exc)
        raise self.retry(exc=exc)

    unprocessed = Parcel.objects.filter(delivery_cost__isnull=True)
    updated_count = 0

    for parcel in unprocessed.iterator():
        # (вес * 0.5 + стоимость * 0.01) * курс
        cost = (
            parcel.weight * Decimal(FORMULA_WEIGHT_COEFFICIENT)
            + parcel.cost * Decimal(FORMULA_COST_COEFFICIENT)
        ) * usd_rate
        parcel.delivery_cost = cost
        parcel.save(update_fields=['delivery_cost', 'updated_at'])
        updated_count += 1

    task_logger.info(
        'Рассчитана стоимость доставки для {updated} посылок (курс: {rate})',
        updated=updated_count,
        rate=usd_rate
    )
    return updated_count