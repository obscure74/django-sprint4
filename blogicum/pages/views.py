"""Представления для статичных страниц."""
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """View для страницы 'О проекте'."""

    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """View для страницы 'Правила'."""

    template_name = 'pages/rules.html'
