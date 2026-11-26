import pytest
from rest_framework.test import APIClient

from parcels.models import Parcel, ParcelType


# ----- Users -----
@pytest.fixture
def owner(django_user_model):
    """Владелец посылки"""
    return django_user_model.objects.create_user(
        email='owner@example.com',
        username='Owner',
        phone_number='+79991112232',
        password='testpass123'
    )

@pytest.fixture
def not_owner(django_user_model):
    """Не владелец посылки"""
    return django_user_model.objects.create_user(
        email='notowner@example.com',
        username='Not_owner',
        phone_number='+79992223344',
        password='testpass123'
    )


# ----- API-клиенты -----

@pytest.fixture
def api_client():
    """Неаутентифицированный DRF-клиент."""
    return APIClient()


@pytest.fixture
def owner_api_client(owner):
    """DRF-клиент от имени владельца."""
    client = APIClient()
    client.force_authenticate(user=owner)
    return client


@pytest.fixture
def not_owner_api_client(not_owner):
    """DRF-клиент от имени другого пользователя."""
    client = APIClient()
    client.force_authenticate(user=not_owner)
    return client


# ----- Parcels -----

@pytest.fixture
def parcel_types(db):
    """Три типа посылки: clothes, electronics, other."""
    types = {}
    for code in ('clothes', 'electronics', 'other'):
        obj, _ = ParcelType.objects.get_or_create(name=code)
        types[code] = obj
    return types

@pytest.fixture
def parcel(db, owner, parcel_types):
    """Посылка без рассчитанной стоимости доставки."""
    return Parcel.objects.create(
        name='Ноутбук',
        weight=10,
        cost=10,
        user=owner,
        parcel_type=parcel_types['other'],
    )

@pytest.fixture
def parcel_with_cost(db, owner, parcel_types):
    """Посылка, у которой стоимость доставки уже рассчитана."""
    return Parcel.objects.create(
        name='Письмо',
        weight=2,
        cost=5,
        user=owner,
        parcel_type=parcel_types['clothes'],
        delivery_cost=100,
    )
