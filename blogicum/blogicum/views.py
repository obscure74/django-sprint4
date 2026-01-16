"""Обработчики для кастомных страниц ошибок."""
from django.shortcuts import render


def page_not_found(request, exception):
    """Обработчик для ошибки 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Обработчик для ошибки 500."""
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    """
    Обработчик для ошибки CSRF 403.
    Обратите внимание: в задании указано 403 CSRF,
    но в шаблонах, вероятно, 'pages/403csrf.html'.
    """
    return render(request, 'pages/403csrf.html', status=403)


def permission_denied(request, exception):
    """Обработчик для ошибки 403 (доступ запрещен)."""
    return render(request, 'pages/403.html', status=403)
