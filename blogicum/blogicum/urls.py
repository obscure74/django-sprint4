from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Аутентификация (встроенная в Django)
    path('auth/', include('django.contrib.auth.urls')),

    # Приложения проекта
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('users/', include('users.urls', namespace='users')),
]

# Обработчик ошибки 403
handler403 = 'blogicum.views.permission_denied'

# Обработчик ошибки 404
handler404 = 'blogicum.views.page_not_found'

# Обработчик ошибки 500
handler500 = 'blogicum.views.server_error'

# Обслуживание медиафайлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
