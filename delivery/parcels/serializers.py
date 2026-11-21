from decimal import Decimal

from rest_framework import serializers


from .models import Parcel, ParcelType
from delivery.constants import (
    PARCEL_MIN_WEIGHT,
    PARCEL_MIN_COST
)


class ParcelTypeSerializer(serializers.ModelSerializer):
    """Справочник типов: id, машинный код и человекочитаемое имя."""

    display_name = serializers.CharField(
        source='get_name_display',
        read_only=True,
    )

    class Meta:
        model = ParcelType
        fields = ('id', 'name', 'display_name')


class ParcelCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации посылки"""

    parcel_type = serializers.SlugRelatedField(
        slug_field='name',
        queryset=ParcelType.objects.all(),
        error_messages={
            'does_not_exist': 'Тип посылки "{value}" не существует.',
        },
    )

    class Meta:
        model = Parcel
        fields = ('id', 'name', 'weight', 'cost', 'parcel_type')
        read_only_fields = ('id',)
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'weight': {'required': True},
            'cost': {'required': True},
        }

    def validate_name(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Название не может быть пустым.')
        return value

    def validate_weight(self, value: Decimal) -> Decimal:
        if value <= PARCEL_MIN_WEIGHT:
            raise serializers.ValidationError(f'Вес должен быть больше {PARCEL_MIN_WEIGHT} кг.')
        return value

    def validate_cost(self, value: Decimal) -> Decimal:
        if value < PARCEL_MIN_COST:
            raise serializers.ValidationError(
                'Стоимость содержимого не может быть отрицательной.'
            )
        return value

    def create(self, validated_data: dict) -> Parcel:
        user = self.context['request'].user
        return Parcel.objects.create(user=user, **validated_data)


class ParcelReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о посылке"""

    parcel_type = serializers.SlugRelatedField(
        slug_field='name',
        queryset=ParcelType.objects.all(),
    )
    delivery_cost = serializers.SerializerMethodField()

    class Meta:
        model = Parcel
        fields = (
            'id',
            'name',
            'weight',
            'cost',
            'parcel_type',
            'delivery_cost',
            'created_at',
        )

    def get_delivery_cost(self, obj: Parcel) -> str | float:
        if obj.delivery_cost is None:
            return 'Не рассчитано'
        return float(obj.delivery_cost)
