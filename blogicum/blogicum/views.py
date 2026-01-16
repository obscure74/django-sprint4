import logging

from django.shortcuts import render

logger = logging.getLogger(__name__)


def page_not_found(request, exception):
    """
    Кастомный обработчик ошибки 404 - Страница не найдена.

    Args:
        request: Объект HttpRequest
        exception: Исключение, вызвавшее ошибку 404

    Returns:
        HttpResponse с кастомной страницей 404
    """
    logger.error(f"404 Error: {request.path} - {exception}")

    context = {
        'title': 'Страница не найдена (404)',
        'path': request.path,
    }

    return render(request, 'pages/404.html', context, status=404)


def server_error(request):
    """
    Кастомный обработчик ошибки 500 - Внутренняя ошибка сервера.

    Args:
        request: Объект HttpRequest

    Returns:
        HttpResponse с кастомной страницей 500
    """
    logger.critical(f"500 Error: {request.path}")

    context = {
        'title': 'Ошибка сервера (500)',
        'support_email': 'support@blogicum.ru',
    }

    return render(request, 'pages/500.html', context, status=500)


def permission_denied(request, exception):
    """
    Кастомный обработчик ошибки 403 - Доступ запрещен.
    Включая ошибки CSRF.

    Args:
        request: Объект HttpRequest
        exception: Исключение PermissionDenied или CsrfError

    Returns:
        HttpResponse с кастомной страницей 403
    """
    logger.warning(f"403 Error: {request.path} - {exception}")

    context = {
        'title': 'Доступ запрещен (403)',
        'login_url': '/auth/login/' if not request.user.is_authenticated else None,
    }

    return render(request, 'pages/403csrf.html', context, status=403)