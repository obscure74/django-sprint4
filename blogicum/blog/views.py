from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()


def index(request):
    """
    Главная страница со списком публикаций.

    Выводит 10 последних постов с пагинацией.

    Context:
        page_obj: Объект страницы с постами
        title: Заголовок страницы
    """
    post_list = Post.objects.select_related(
        'author', 'category', 'location'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).order_by('-pub_date')

    # Аннотируем количество комментариев
    post_list = post_list.annotate(comment_count=Count('comments'))

    # Пагинация: 10 постов на странице
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'Главная страница',
    }

    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """
    Отображает детальную страницу поста по ID.

    Args:
        post_id: ID поста для отображения

    Context:
        post: Объект публикации
        form: Форма для добавления комментария
        comments: Комментарии к посту
    """
    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location')
        .prefetch_related('comments_author'),
        id=post_id
    )

    # Проверяем, может ли пользователь видеть пост
    can_view = (
        post.is_published
        and post.pub_date <= timezone.now()
        and (not post.category or post.category.is_published)
    )

    # Автор может видеть все свои посты
    if not can_view and request.user != post.author:
        return render(request, 'pages/404.html', status=404)

    comments = post.comments.all()
    form = None

    # Форма комментария только для авторизованных
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(request, 'Комментарий добавлен!')
                return redirect('blog:post_detail', post_id=post_id)
        else:
            form = CommentForm()

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }

    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """
    Отображает страницу категории с постами.

    Args:
        category_slug: slug категории для отображения

    Context:
        page_obj: Объект страницы с постами
        category: Объект категории
    """
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = Post.objects.select_related(
        'author', 'location'
    ).filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')

    # Аннотируем количество комментариев
    post_list = post_list.annotate(comment_count=Count('comments'))

    # Пагинация: 10 постов на странице
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'category': category,
    }

    return render(request, 'blog/category.html', context)


@login_required
def create_post(request):
    """
    Создание новой публикации.

    Доступно только авторизованным пользователям.
    После создания редирект на профиль пользователя.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # Автор может видеть отложенные посты сразу
            post.save()

            messages.success(request, 'Пост успешно создан!')
            return redirect('users:profile', username=request.user.username)
    else:
        form = PostForm()

    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_id):
    """
    Редактирование существующей публикации.

    Доступно только автору публикации.
    Использует тот же шаблон, что и create_post.

    Args:
        post_id: ID публикации для редактирования
    """
    post = get_object_or_404(Post, pk=post_id)

    # Проверка прав: только автор может редактировать
    if post.author != request.user:
        messages.error(request, 'Вы не можете редактировать этот пост.')
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост успешно отредактирован!')
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)

    context = {'form': form, 'is_edit': True}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    """
    Удаление публикации.

    Доступно только автору публикации.
    Перед удалением показывает страницу подтверждения.

    Args:
        post_id: ID публикации для удаления
    """
    post = get_object_or_404(Post, pk=post_id)

    # Проверка прав: только автор может удалить
    if post.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост успешно удален!')
        return redirect('users:profile', username=request.user.username)

    # GET запрос: показываем страницу подтверждения
    context = {'post': post}
    return render(request, 'blog/detail.html', context)


@login_required
def add_comment(request, post_id):
    """
    Добавление комментария к публикации.

    Доступно только авторизованным пользователям.

    Args:
        post_id: ID публикации
    """
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """
    Редактирование комментария.

    Доступно только автору комментария.

    Args:
        post_id: ID публикации
        comment_id: ID комментария
    """
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)

    # Проверка прав: только автор может редактировать
    if comment.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комментарий отредактирован!')
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    context = {
        'form': form,
        'comment': comment,
        'post': comment.post,
    }

    return render(request, 'blog/comment_edit.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    """
    Удаление комментария.

    Доступно только автору комментария.
    Перед удалением показывает страницу подтверждения.

    Args:
        post_id: ID публикации
        comment_id: ID комментария
    """
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)

    # Проверка прав: только автор может удалить
    if comment.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий удален!')

    return redirect('blog:post_detail', post_id=post_id)
