from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Конфигурация приложения Blog."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = 'Блог'
