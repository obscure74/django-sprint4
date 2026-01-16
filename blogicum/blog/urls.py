"""URL-маршруты для приложения blog."""
from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),

    # Детальная страница поста
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),

    # Страница категории
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'),

    # Создание поста
    path('posts/create/', views.create_post, name='post_create'),

    # Редактирование поста
    path('posts/<int:post_id>/edit/', views.edit_post, name='post_edit'),

    # Удаление поста
    path('posts/<int:post_id>/delete/', views.delete_post, name='post_delete'),

    # Комментарии
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.edit_comment,
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.delete_comment,
        name='delete_comment'
    ),
]
