"""Представления для приложения blog."""
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post
from .forms import UserEditForm

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
    ).select_related('author', 'location')
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
            if post.pub_date > timezone.now():
                post.is_published = True
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm(initial={'pub_date': timezone.now()})
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Редактирование существующей публикации."""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)
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

    # Комментарии только опубликованные
    comments = post.comments.filter(is_published=True)

    # Форма для комментария
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
        post_id=post_id
    )

    # Проверяем, что пользователь является автором комментария
    if comment.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        # GET запрос - показываем форму для редактирования
        form = CommentForm(instance=comment)
        return render(request, 'blog/edit_comment.html', {
            'form': form,
            'post_id': post_id,
            'comment_id': comment_id
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
        return redirect('blog:profile', username=username)
    return render(request, 'blog/detail.html', {'post': post})


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    post = get_object_or_404(Post, id=post_id)
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
    else:
        # GET запрос - показываем страницу подтверждения
        return render(request, 'blog/delete_comment.html', {
            'comment': comment,
            'post': post
        })


def profile(request, username):
    """Страница профиля пользователя."""
    profile_user = get_object_or_404(User, username=username)

    # Для автора показываем все посты, для других - только опубликованные
    if request.user == profile_user:
        post_list = profile_user.posts.all()
    else:
        post_list = profile_user.posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    """Редактирование профиля пользователя."""
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен.')
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'blog/user.html', {'form': form})
