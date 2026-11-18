from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя"""

    phone_number = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        verbose_name='Номер телефона'
    )
    birthday = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения'
    )
