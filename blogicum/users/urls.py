from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Регистрация
    path('registration/', views.signup, name='signup'),

    # Профиль пользователя
    path('profile/<str:username>/', views.profile, name='profile'),

    # Редактирование профиля (только через админку или формы Django)
    # Ссылки на смену пароля доступны через django.contrib.auth.urls

    # Кастомная страница смены пароля (опционально)
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='users/password_change_form.html'
        ),
        name='password_change'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
]
