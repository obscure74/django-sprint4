"""Представления для статичных страниц."""
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """Представление для страницы 'О проекте'."""

    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """Представление для страницы 'Правила'."""

    template_name = 'pages/rules.html'
