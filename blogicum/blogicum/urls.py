"""Основной файл URL-маршрутов проекта."""
from blog.views import RegistrationView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

# Обработчики ошибок
handler403 = 'blog.views.csrf_failure'
handler404 = 'blog.views.page_not_found'
handler500 = 'blog.views.server_error'

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
