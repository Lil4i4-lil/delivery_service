from django.urls import path

from .views import (
    parcel_type_list,
    ParcelDetailView,
    ParcelListCreateView
)

app_name = 'parcels'


urlpatterns = [
    path('parcel-types/', parcel_type_list, name='parcel-types-list'),
    path('parcels/', ParcelListCreateView.as_view(), name='parcels-list-create'),
    path('parcels/<uuid:pk>/', ParcelDetailView.as_view(), name='parcels-detail'),
]
