import uuid

from django.conf import settings
from django.db import models

from delivery.constants import (
    PARCEL_NAME_MAX_LENGTH,
    PARCEL_TYPE_NAME_MAX_LENGTH,
    PARCEL_TYPE_CLOTHES,
    PARCEL_TYPE_ELECTRONICS,
    PARCEL_TYPE_OTHER
)
from users.models import User


PARCEL_TYPE_CHOICES = [
    (PARCEL_TYPE_CLOTHES, 'Одежда'),
    (PARCEL_TYPE_ELECTRONICS , 'Электроника'),
    (PARCEL_TYPE_OTHER, 'Другое'),
]


class ParcelType(models.Model):
    """Модель типа посылки"""
    name = models.CharField(
        max_length=PARCEL_TYPE_NAME_MAX_LENGTH,
        choices=PARCEL_TYPE_CHOICES,
        unique=True,
        verbose_name='Название',
    )

    class Meta:
        verbose_name = 'Тип посылки'
        verbose_name_plural = 'Типы посылок'
        ordering = ['id']

    def __str__(self) -> str:
        return self.name


class Parcel(models.Model):
    """Модель посылки"""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Идентификатор',
    )
    name = models.CharField(
        max_length=PARCEL_NAME_MAX_LENGTH,
        verbose_name = 'Название',
    )
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        verbose_name='Вес, кг',
    )
    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Стоимость, USD',
    )
    delivery_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Стоимость доставки, RUB',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    ) # Удалить

    parcel_type = models.ForeignKey(
        ParcelType,
        on_delete=models.PROTECT,
        related_name='parcels',
        verbose_name='Тип',
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_parcels',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Посылка'
        verbose_name_plural = 'Посылки'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(weight__gt=0),
                name='weight_positive',
            ),
            models.CheckConstraint(
                condition=models.Q(cost__gte=0),
                name='cost_non_negative',
            ),
        ]
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self) -> str:
        return f'{self.name} ({self.id})'
