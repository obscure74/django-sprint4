"""Представления для статичных страниц."""
from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError


def csrf_failure(request, reason=''):
    """Кастомная страница ошибки 403 CSRF."""
    return HttpResponseForbidden(
        render(request, 'pages/403csrf.html', status=403)
    )


def page_not_found(request, exception):
    """Кастомная страница ошибки 404."""
    return HttpResponseNotFound(render(request, 'pages/404.html'))


def server_error(request):
    """Кастомная страница ошибки 500."""
    return HttpResponseServerError(render(request, 'pages/500.html'))


class AboutView(TemplateView):
    """View для страницы 'О проекте'."""

    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """View для страницы 'Правила'."""

    template_name = 'pages/rules.html'
