"""Представления для приложения blog."""
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()


def index(request):
    """Главная страница с пагинацией (10 постов на странице)."""
    post_list = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).select_related(
        'category', 'author', 'location'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug):
    """Страница категории с пагинацией."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = category.posts.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('author', 'location').annotate(
        comment_count=Count('comments')
    )

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


@login_required
def create_post(request):
    """Создание новой публикации."""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # Проверяем, является ли пост отложенным
            if post.pub_date > timezone.now():
                # Отложенный пост - не публикуем сразу
                post.is_published = True

            post.save()

            # Перенаправляем на страницу профиля пользователя
            return redirect(
                'users:profile',
                username=request.user.username
            )
    else:
        # Устанавливаем текущую дату и время по умолчанию
        form = PostForm(initial={'pub_date': timezone.now()})

    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Редактирование существующей публикации."""
    post = get_object_or_404(Post, id=post_id)
    # Проверяем, что пользователь является автором
    if post.author != request.user:
        # Если не автор - перенаправляем на страницу поста
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)

    # Используем тот же шаблон, что и для создания
    return render(request, 'blog/create.html', {'form': form})


def post_detail(request, post_id):
    """Детальная страница публикации."""
    post = get_object_or_404(Post, id=post_id)

    # Проверяем доступ к посту
    if not post.is_published or post.pub_date > timezone.now():
        # Если пост не опубликован или отложен
        if request.user != post.author:
            # И пользователь не автор - показываем 404
            raise Http404("Публикация не найдена")

    # Комментарии
    comments = post.comments.filter(is_published=True)

    # Форма для комментариев (если пользователь авторизован)
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': comment_form,
    }
    return render(request, 'blog/detail.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария к публикации."""
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    comment = get_object_or_404(
        Comment, 
        id=comment_id, 
        post_id=post_id,
    )

    if comment.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/edit_comment.html', {
        'form': form,
        'post': comment.post,
        'comment': comment,
    })


@login_required
def delete_post(request, post_id):
    """Удаление публикации."""
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        username = post.author.username
        post.delete()
        return redirect('users:profile', username=username)

    # Для GET запроса показываем страницу подтверждения
    return render(request, 'blog/detail.html', {'post': post})


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    comment = get_object_or_404(
        Comment, 
        id=comment_id, 
        post_id=post_id
    )

    if comment.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/delete_comment.html', {
        'post': comment.post,
        'comment': comment,
    })


def profile_redirect(request, username):
    """Перенаправление с blog:profile на users:profile."""
    return redirect('users:profile', username=username)
