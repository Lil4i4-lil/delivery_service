from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для кастомного пользователя."""

    list_display = (
        'id',
        'username',
        'phone_number',
        'birthday',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
    )
    list_filter = BaseUserAdmin.list_filter + ('birthday',)
    search_fields = ('username', 'phone_number', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'birthday'),
        }),
        ('Права', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'phone_number',
                'birthday',
                'email',
                'first_name',
                'last_name',
                'password1',
                'password2',
                'is_staff',
                'is_superuser',
            ),
        }),
    )