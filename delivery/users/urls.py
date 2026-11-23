from django.urls import include, path

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),  # JWT-авторизация
    path('accounts/', include('allauth.urls')),  # OAUTH-авторизация
]
