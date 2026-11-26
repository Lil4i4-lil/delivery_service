from django_filters.rest_framework import DjangoFilterBackend
from loguru import logger
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, throttle_scope
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Parcel, ParcelType
from .permissions import isOwner
from .serializers import ParcelCreateSerializer, ParcelReadSerializer, ParcelTypeSerializer
from .tasks import calculate_delivery_costs


@api_view(['GET'])
@throttle_scope('parcel_types_list')
def parcel_type_list(request: Request) -> Response:
    """Получение списка типов посылок"""

    parcel_types = ParcelType.objects.all()
    serializer = ParcelTypeSerializer(parcel_types, many=True)
    return Response(serializer.data)


class ParcelListCreateView(generics.ListCreateAPIView):
    """Создание и получение списка посылок"""

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'delivery_cost', 'parcel_type__name')
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    throttle_scope = 'parcels_list_create'

    def get_queryset(self):
        qs = (
            Parcel.objects.filter(user=self.request.user)
            .select_related('parcel_type')
            .order_by('-created_at')
        )

        parcel_type = self.request.query_params.get('parcel_type')
        if parcel_type:
            qs = qs.filter(parcel_type__name=parcel_type)

        calculated = self.request.query_params.get('calculated')
        if calculated == 'true':
            qs = qs.filter(delivery_cost__isnull=False)
        elif calculated == 'false':
            qs = qs.filter(delivery_cost__isnull=True)

        return qs

    def get_serializer_class(self):
        return ParcelCreateSerializer if self.request.method == 'POST' else ParcelReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logger.bind(component='parcels').info(
            'Создание посылки: user_id={user_id}, type={parcel_type}, weight={weight}',
            user_id=request.user.id,
            parcel_type=serializer.validated_data.get('parcel_type'),
            weight=serializer.validated_data.get('weight'),
        )

        parcel = serializer.save()

        logger.bind(component='parcels').info(
            'Посылка создана: id={parcel_id}, user_id={user_id}',
            parcel_id=parcel.id,
            user_id=request.user.id,
        )

        return Response(
            ParcelReadSerializer(parcel, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class ParcelDetailView(generics.RetrieveAPIView):
    """Получение детальной информации о посылке по ее uuid"""

    permission_classes = [isOwner]
    throttle_scope = 'parcels_detail'

    serializer_class = ParcelReadSerializer
    queryset = Parcel

    # def get_queryset(self):
    #     return Parcel.objects.filter(user=self.request.user).select_related('parcel_type')


class RecalculateDeliveryCostsView(APIView):
    """Ручной запуск пересчёта стоимости доставки"""

    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        calculate_delivery_costs.delay()
        return Response(
            {'status': 'Задача поставлена в очередь'},
            status=status.HTTP_202_ACCEPTED,
        )
