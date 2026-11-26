from decimal import Decimal
from unittest.mock import patch

import pytest
from rest_framework import status

from parcels.models import Parcel, ParcelType
from parcels.tasks import calculate_delivery_costs

# ----- Модели -----

@pytest.mark.django_db
class TestParcelTypeModel:
    def test_three_types_created(self, parcel_types):
        assert ParcelType.objects.count() == 3
        assert set(ParcelType.objects.values_list('name', flat=True)) == {
            'clothes', 'electronics', 'other',
        }


@pytest.mark.django_db
class TestParcelModel:
    def test_calculate_delivery_cost_formula(self, parcel):
        # (10 * 0.5 + 10 * 0.01) * 90 = (5 + 0.1) * 90 = 459
        result = parcel.calculate_delivery_cost(Decimal('90'))
        assert result == Decimal('459')

    def test_default_delivery_cost_is_none(self, parcel):
        assert parcel.delivery_cost is None


# ----- API: типы посылок -----

@pytest.mark.django_db
class TestParcelTypeAPI:
    URL = '/api/v1/parcel-types/'

    def test_unauthorized_returns_200(self, api_client, parcel_types):
        response = api_client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK

    def test_returns_all_types(self, owner_api_client, parcel_types):
        response = owner_api_client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        names = {item['name'] for item in data}
        assert names == {'clothes', 'electronics', 'other'}

    def test_display_name_in_response(self, owner_api_client, parcel_types):
        response = owner_api_client.get(self.URL)
        clothes = next(t for t in response.json() if t['name'] == 'clothes')
        assert clothes['display_name'] == 'Одежда'


# ----- API: создание посылки -----

@pytest.mark.django_db
class TestParcelCreateAPI:
    URL = '/api/v1/parcels/'

    def _payload(self, **overrides):
        data = {
            'name': 'Ноутбук',
            'weight': '1.5',
            'cost': '1200.00',
            'parcel_type': 'electronics',
        }
        data.update(overrides)
        return data

    def test_unauthorized_returns_401_or_403(self, api_client, parcel_types):
        response = api_client.post(self.URL, self._payload(), format='json')
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

    def test_creates_parcel_for_current_user(
        self, owner_api_client, owner, parcel_types,
    ):
        response = owner_api_client.post(
            self.URL, self._payload(), format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED

        parcel = Parcel.objects.get(id=response.json()['id'])
        assert parcel.user == owner
        assert parcel.name == 'Ноутбук'
        assert parcel.weight == Decimal('1.5')
        assert parcel.cost == Decimal('1200.00')
        assert parcel.delivery_cost is None

    def test_response_contains_not_calculated_cost(
        self, owner_api_client, parcel_types,
    ):
        response = owner_api_client.post(
            self.URL, self._payload(), format='json',
        )
        assert response.json()['delivery_cost'] == 'Не рассчитано'

    def test_user_cannot_be_overridden(
        self, owner_api_client, owner, not_owner, parcel_types,
    ):
        """Даже если клиент подсунет user в теле — поле игнорируется."""
        response = owner_api_client.post(
            self.URL,
            self._payload(user=not_owner.id),
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        parcel = Parcel.objects.get(id=response.json()['id'])
        assert parcel.user == owner

    @pytest.mark.parametrize('weight', ['0', '-1', '150'])
    def test_invalid_weight_returns_400(
        self, owner_api_client, parcel_types, weight,
    ):
        response = owner_api_client.post(
            self.URL, self._payload(weight=weight), format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'weight' in response.json()

    @pytest.mark.parametrize('cost', ['-1', '-100'])
    def test_negative_cost_returns_400(
        self, owner_api_client, parcel_types, cost,
    ):
        response = owner_api_client.post(
            self.URL, self._payload(cost=cost), format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cost' in response.json()

    def test_blank_name_returns_400(self, owner_api_client, parcel_types):
        response = owner_api_client.post(
            self.URL, self._payload(name=''), format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.json()

    def test_unknown_parcel_type_returns_400(
        self, owner_api_client, parcel_types,
    ):
        response = owner_api_client.post(
            self.URL, self._payload(parcel_type='unknown'), format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'parcel_type' in response.json()


# ----- API: список -----

@pytest.mark.django_db
class TestParcelListAPI:
    URL = '/api/v1/parcels/'

    def test_returns_only_own_parcels(
        self, owner_api_client, owner, not_owner, parcel_types,
    ):
        own = Parcel.objects.create(
            user=owner, name='Своя',
            weight=1, cost=1, parcel_type=parcel_types['other'],
        )
        Parcel.objects.create(
            user=not_owner, name='Чужая',
            weight=1, cost=1, parcel_type=parcel_types['other'],
        )
        response = owner_api_client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data['results'] if 'results' in data else data
        assert len(items) == 1
        assert items[0]['id'] == str(own.id)

    def test_filter_by_parcel_type(
        self, owner_api_client, owner, parcel_types,
    ):
        Parcel.objects.create(
            user=owner, name='A',
            weight=1, cost=1, parcel_type=parcel_types['clothes'],
        )
        Parcel.objects.create(
            user=owner, name='B',
            weight=1, cost=1, parcel_type=parcel_types['electronics'],
        )
        response = owner_api_client.get(self.URL, {'parcel_type': 'clothes'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data['results'] if 'results' in data else data
        assert len(items) == 1
        assert items[0]['name'] == 'A'

    def test_filter_by_calculated_false(
        self, owner_api_client, owner, parcel, parcel_with_cost,
    ):
        response = owner_api_client.get(self.URL, {'calculated': 'false'})
        data = response.json()
        items = data['results'] if 'results' in data else data
        assert len(items) == 1
        assert items[0]['name'] == parcel.name


# ----- API: детали -----

@pytest.mark.django_db
class TestParcelDetailAPI:
    def _url(self, parcel_id):
        return f'/api/v1/parcels/{parcel_id}/'

    def test_owner_gets_parcel(self, owner_api_client, parcel):
        response = owner_api_client.get(self._url(parcel.id))
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['id'] == str(parcel.id)
        assert data['name'] == parcel.name

    def test_non_owner_gets_404(
        self, not_owner_api_client, parcel,
    ):
        response = not_owner_api_client.get(self._url(parcel.id))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_not_calculated_cost_in_response(
        self, owner_api_client, parcel,
    ):
        response = owner_api_client.get(self._url(parcel.id))
        assert response.json()['delivery_cost'] == 'Не рассчитано'

    def test_calculated_cost_in_response(
        self, owner_api_client, parcel_with_cost,
    ):
        response = owner_api_client.get(self._url(parcel_with_cost.id))
        assert float(response.json()['delivery_cost']) == 100.0


# ----- Celery task -----

@pytest.mark.django_db
class TestCalculateDeliveryCostsTask:
    def test_updates_only_unprocessed_parcels(
        self, parcel, parcel_with_cost,
    ):
        with patch('parcels.tasks.get_usd_rate', return_value=Decimal('90')):
            updated = calculate_delivery_costs()

        assert updated == 1
        parcel.refresh_from_db()
        parcel_with_cost.refresh_from_db()
        # (10 * 0.5 + 10 * 0.01) * 90 = 459
        assert parcel.delivery_cost == Decimal('459')
        assert parcel_with_cost.delivery_cost == Decimal('100')

    def test_does_nothing_when_no_unprocessed(self, parcel_with_cost):
        with patch('parcels.tasks.get_usd_rate', return_value=Decimal('90')):
            updated = calculate_delivery_costs()

        assert updated == 0

    def test_returns_zero_when_no_parcels(self, db):
        with patch('parcels.tasks.get_usd_rate', return_value=Decimal('90')):
            updated = calculate_delivery_costs()

        assert updated == 0
