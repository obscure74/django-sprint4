"""Представления для статичных страниц."""

from django.http import (HttpResponseForbidden, HttpResponseNotFound,
                         HttpResponseServerError)
from django.shortcuts import render
from django.views.generic import TemplateView


def csrf_failure(request, reason='', **kwargs):
    """Кастомная страница ошибки 403 CSRF."""
    return HttpResponseForbidden(render(request, 'pages/403csrf.html'))


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
