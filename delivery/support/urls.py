from django.urls import path

from .views import SupportAskView

urlpatterns = [
    path('', SupportAskView.as_view()),
]
