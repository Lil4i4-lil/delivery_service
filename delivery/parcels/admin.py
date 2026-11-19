from django.contrib import admin

from .models import Parcel, ParcelType


@admin.register(ParcelType)
class ParcelTypeAdmin(admin.ModelAdmin):
    """Админка для справочника типов посылок."""

    list_display = ('id', 'name')
    ordering = ('id',)
    search_fields = ('name',)


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    """Админка для посылок."""

    list_display = (
        'id',
        'name',
        'user',
        'parcel_type',
        'weight',
        'cost',
        'created_at',
    )
    list_filter = (
        'parcel_type',
        'created_at',
    )
    search_fields = ('id', 'name', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_select_related = ('user', 'parcel_type')

    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'user', 'parcel_type'),
        }),
        ('Параметры посылки', {
            'fields': ('weight', 'cost'),
        }),
        ('Служебное', {
            'fields': ('created_at', 'updated_at'),
        }),
    )