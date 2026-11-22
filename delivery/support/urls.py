from django.urls import include, path

from .views import SupportAskView


urlpatterns = [
    path('', SupportAskView.as_view()),
]