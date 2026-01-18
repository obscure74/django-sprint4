"""Основной файл URL-маршрутов проекта."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from blog.views import RegistrationView

# Обработчики ошибок
handler403 = 'pages.views.csrf_failure'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
]


# Медиафайлы в режиме отладки
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    # Также обслуживаем файлы из STATICFILES_DIRS
    urlpatterns += staticfiles_urlpatterns()
