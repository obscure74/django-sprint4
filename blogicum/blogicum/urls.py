"""Основной файл URL-маршрутов проекта."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as users_views

handler403 = 'blogicum.views.csrf_failure'
handler404 = 'blogicum.views.page_not_found'
handler500 = 'blogicum.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),

    # Стандартные пути аутентификации Django
    path('auth/', include('django.contrib.auth.urls')),

    # Прямой путь для регистрации без пространства имен
    path('registration/', users_views.registration, name='registration'),

    # Профиль пользователя - тоже прямой путь
    path('profile/<str:username>/', users_views.profile, name='profile'),

    # Остальные пути через пространства имен
    path('', include('users.urls', namespace='users')),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
]

# Медиафайлы в режиме отладки
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
