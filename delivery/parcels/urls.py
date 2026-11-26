from django.urls import path

from .views import (
    ParcelDetailView,
    ParcelListCreateView,
    RecalculateDeliveryCostsView,
    parcel_type_list,
)

app_name = 'parcels'


urlpatterns = [
    path('parcel-types/', parcel_type_list, name='parcel-types-list'),
    path('parcels/', ParcelListCreateView.as_view(), name='parcels-list-create'),
    path('parcels/<uuid:pk>/', ParcelDetailView.as_view(), name='parcels-detail'),
    path(
        'parcels/recalculate-costs/',
        RecalculateDeliveryCostsView.as_view(),
        name='parcel-recalculate-costs',
    ),
]
