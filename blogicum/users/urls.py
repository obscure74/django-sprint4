"""URL-маршруты для приложения users."""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path(
        'profile/<str:username>/edit/',
        views.edit_profile,
        name='edit_profile'
    ),
    path(
        'profile/<str:username>/password/',
        views.change_password,
        name='change_password'
    ),
]
