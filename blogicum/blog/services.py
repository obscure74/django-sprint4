"""Вспомогательные функции для приложения blog."""

from django.core.paginator import Paginator
from django.db.models import Count

from .constants import POSTS_PER_PAGE


def get_paginated_page(request, queryset, per_page=POSTS_PER_PAGE):
    """Возвращает пагинированную страницу для queryset."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def filter_and_annotate_posts(
    queryset,
    filter_published=True,
    annotate_comments=True
):
    """
    Фильтрует и аннотирует посты.

    Args:
        queryset: QuerySet постов
        filter_published: Фильтровать ли только опубликованные
        annotate_comments: Добавлять ли аннотацию с количеством комментариев

    Returns:
        QuerySet: Обработанный QuerySet
    """
    if filter_published:
        queryset = queryset.filter(is_published=True)

    if annotate_comments:
        queryset = queryset.annotate(comment_count=Count('comments'))

    return queryset.select_related('category', 'location', 'author')
