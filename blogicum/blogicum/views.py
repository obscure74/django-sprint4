"""Обработчики для кастомных страниц ошибок."""
from django.http import HttpResponseForbidden
from django.shortcuts import render


def page_not_found(request, exception):
    """Обработчик для ошибки 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Обработчик для ошибки 500."""
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    """Обработчик для ошибки CSRF 403."""
    return render(request, 'pages/403csrf.html', status=403)


def permission_denied(request, exception):
    """Обработчик для ошибки 403 (доступ запрещен)."""
    return HttpResponseForbidden('Доступ запрещен')
