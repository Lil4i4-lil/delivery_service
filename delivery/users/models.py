from django.contrib.auth.models import AbstractUser
from django.db import models

from delivery.constants import (
    PHONE_NUMBER_MAX_LENGTH,
)


class User(AbstractUser):
    """Кастомная модель пользователя"""

    phone_number = models.CharField(
        max_length=PHONE_NUMBER_MAX_LENGTH, null=True, blank=True, verbose_name='Номер телефона'
    )
    birthday = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
