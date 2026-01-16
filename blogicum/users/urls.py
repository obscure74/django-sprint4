"""URL-маршруты для приложения users."""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('registration/', views.registration, name='registration'),
    path('profile/<str:username>/', views.profile, name='profile'),
]
