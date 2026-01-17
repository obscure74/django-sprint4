"""URL-маршруты для приложения users."""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('registration/', views.registration, name='registration'),
    
    # Профиль пользователя
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path(
        'profile/<str:username>/password/',
        views.change_password,
        name='change_password'
    ),
]
