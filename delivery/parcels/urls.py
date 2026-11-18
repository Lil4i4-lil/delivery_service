from django.urls import path

from .views import (
    parcel_type_list,
    ParcelDetailView,
    ParcelListCreateView
)

app_name = 'parcels'


urlpatterns = [
    path('parcel-type/', parcel_type_list, name='parcel-type-list'),
    path('parcels/', ParcelListCreateView.as_view(), name='parcel-list-create'),
    path('parcels/<uuid:pk>/', ParcelDetailView.as_view(), name='parcel-detail'),
]
