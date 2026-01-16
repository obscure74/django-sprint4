from django.views.generic import TemplateView


class AboutView(TemplateView):
    """
    Представление для страницы "О проекте".

    Использует шаблон: templates/pages/about.html
    """
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """
    Представление для страницы "Правила".

    Использует шаблон: templates/pages/rules.html
    """
    template_name = 'pages/rules.html'
