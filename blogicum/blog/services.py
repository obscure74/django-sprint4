"""Вспомогательные функции для приложения blog."""

from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from .constants import POSTS_PER_PAGE


def get_paginated_page(request, queryset, per_page=POSTS_PER_PAGE):
    """Возвращает пагинированную страницу для queryset."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def filter_and_annotate_posts(queryset, filter_published=True):
    """
    Фильтрует и аннотирует посты.

    Args:
        queryset: QuerySet постов
        filter_published: Если True, фильтрует только опубликованные посты

    Returns:
        QuerySet: Обработанный QuerySet
    """
    if filter_published:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    queryset = queryset.select_related('category', 'location', 'author')
    queryset = queryset.annotate(comment_count=Count('comments'))
    queryset = queryset.order_by('-pub_date')

    return queryset
