from django.urls import path

from .views import (LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView,)

app_name = 'users'

urlpatterns = [
    path('users/register', RegistrationAPIView.as_view()),
    path('users/login', LoginAPIView.as_view()),
    path('users/authUser', UserRetrieveUpdateAPIView.as_view()),
]