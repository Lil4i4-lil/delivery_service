from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Parcel, ParcelType
from .permissions import isOwner
from .serializers import ParcelTypeSerializer, ParcelCreateSerializer, ParcelReadSerializer


@api_view(['GET'])
def parcel_type_list(request: Request) -> Response:
    parcel_types = ParcelType.objects.all()
    serializer = ParcelTypeSerializer(parcel_types, many=True)
    return Response(serializer.data)


class ParcelListCreateView(generics.ListCreateAPIView):
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'parcel_type__name')

    permission_classes = [permissions.IsAuthenticated]

    pagination_class = PageNumberPagination

    def get_queryset(self):
        qs = (
            Parcel.objects
            .filter(user=self.request.user)
            .select_related('parcel_type')
            .order_by('-created_at')
        )

        parcel_type = self.request.query_params.get('parcel_type')
        if parcel_type:
            qs = qs.filter(parcel_type__name=parcel_type)

        calculated = self.request.query_params.get('calculated')
        if calculated == 'true':
            qs = qs.filter(delivery_cost_rub__isnull=False)
        elif calculated == 'false':
            qs = qs.filter(delivery_cost_rub__isnull=True)

        return qs

    def get_serializer_class(self):
        return (
            ParcelCreateSerializer
            if self.request.method == 'POST'
            else ParcelReadSerializer
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        parcel = serializer.save()
        return Response(
            ParcelReadSerializer(parcel, context={'request': request}).data,
            status=201,
        )


class ParcelDetailView(generics.RetrieveAPIView):
    permission_classes = [isOwner]
    serializer_class = ParcelReadSerializer
    queryset = Parcel

    # def get_queryset(self):
    #     return Parcel.objects.filter(user=self.request.user).select_related('parcel_type')
