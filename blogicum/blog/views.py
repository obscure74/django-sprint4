"""Представления для приложения blog."""

from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView

from .constants import POSTS_PER_PAGE
from .forms import CommentForm, PostForm, RegistrationForm, UserEditForm
from .models import Category, Comment, Post
from .services import get_paginated_page

User = get_user_model()


def index(request):
    """Главная страница."""
    post_list = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('category', 'location', 'author')

    post_list = post_list.annotate(comment_count=Count('comments'))
    post_list = post_list.order_by('-pub_date')

    page_obj = get_paginated_page(request, post_list, POSTS_PER_PAGE)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug):
    """Посты категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = category.posts.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('category', 'location', 'author')

    post_list = post_list.annotate(comment_count=Count('comments'))
    post_list = post_list.order_by('-pub_date')

    page_obj = get_paginated_page(request, post_list, POSTS_PER_PAGE)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj,
    })


def post_detail(request, post_id):
    """Детали поста."""
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        id=post_id
    )

    if request.user != post.author:
        if (not post.is_published
                or not post.category.is_published
                or post.pub_date > timezone.now()):
            raise Http404("Пост не найден")

    comments = post.comments.select_related('author').all()
    form = CommentForm() if request.user.is_authenticated else None

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


def profile_view(request, username):
    """Страница пользователя с пагинацией."""
    user = get_object_or_404(User, username=username)

    if request.user == user:
        post_list = user.posts.all()
    else:
        post_list = user.posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    post_list = post_list.annotate(comment_count=Count('comments'))
    post_list = post_list.select_related('category', 'location')
    post_list = post_list.order_by('-pub_date')

    page_obj = get_paginated_page(request, post_list, POSTS_PER_PAGE)
    return render(request, 'blog/profile.html', {
        'profile': user,
        'page_obj': page_obj,
    })


class RegistrationView(CreateView):
    """Регистрация."""

    form_class = RegistrationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля (для текущего пользователя)."""

    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', post_id=post.id)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.id}
        )


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление поста."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Добавление комментария."""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return (
            reverse(
                'blog:post_detail',
                kwargs={'post_id': self.kwargs['post_id']}
            ) + f'#comment_{self.object.id}'
        )


class CommentMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Миксин для работы с комментариями."""

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        comment = self.get_object()
        return redirect('blog:post_detail', post_id=comment.post.id)


class CommentUpdateView(CommentMixin, UpdateView):
    """Редактирование комментария."""

    template_name = 'blog/comment.html'

    def get_success_url(self):
        return (
            reverse(
                'blog:post_detail',
                kwargs={'post_id': self.object.post.id}
            ) + f'#comment_{self.object.id}'
        )


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.id}
        )
