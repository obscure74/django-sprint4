"""Представления для приложения blog."""
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import CommentForm, PostForm, RegistrationForm, UserEditForm
from .models import Category, Comment, Post

User = get_user_model()


def csrf_failure(request, reason='', **kwargs):
    """Кастомная страница ошибки 403 CSRF."""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    """Кастомная страница ошибки 404."""
    return HttpResponseNotFound(render(request, 'pages/404.html'))


def server_error(request):
    """Кастомная страница ошибки 500."""
    return HttpResponseServerError(render(request, 'pages/500.html'))


def index(request):
    """Главная страница."""
    post_list = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug):
    """Посты категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = category.posts.select_related(
        'author', 'location'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

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

    if request.user == post.author:
        pass
    else:
        if not post.is_published or not post.category.is_published:
            raise Http404("Пост не найден")
        if post.pub_date > timezone.now():
            raise Http404("Пост не найден")

    comments = post.comments.select_related('author').all()
    form = CommentForm() if request.user.is_authenticated else None

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


def profile_view(request, username):
    """
    Страница пользователя с пагинацией.

    Доступна всем пользователям, но показывает разный контент:
    - Владелец профиля видит все свои посты
    - Остальные видят только опубликованные посты
    """
    user = get_object_or_404(User, username=username)

    # Для владельца профиля показываем все посты
    # Для остальных - только опубликованные
    if request.user == user:
        post_list = user.posts.all().select_related(
            'category', 'location'
        ).order_by('-pub_date')
    else:
        post_list = user.posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).select_related('category', 'location').order_by('-pub_date')

    # Аннотируем количество комментариев
    post_list = post_list.annotate(comment_count=Count('comments'))

    # Пагинация
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


def edit_profile(request, username=None):
    """Редактирование профиля."""
    if username is None:
        # Редактирование своего профиля
        user = request.user
    else:
        # Редактирование чужого профиля - проверяем права
        user = get_object_or_404(User, username=username)
        if request.user != user:
            # Не автор - перенаправляем на страницу профиля
            messages.error(
                request, 'Вы можете редактировать только свой профиль.'
            )
            return redirect('blog:profile', username=username)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('blog:profile', username=user.username)
    else:
        form = UserEditForm(instance=user)

    return render(request, 'blog/user.html', {'form': form})


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
        """Возвращает текущего пользователя."""
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
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    raise_exception = False

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        """Перенаправляем на страницу поста при отсутствии прав."""
        post = self.get_object()
        return redirect('blog:post_detail', post_id=post.id)

    def get_success_url(self):
        return reverse_lazy(
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


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Добавление комментария."""

    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        """Проверяем существование поста перед обработкой."""
        post_id = self.kwargs['post_id']
        if not Post.objects.filter(id=post_id).exists():
            raise Http404("Пост не найден")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)

    def get_success_url(self):
        return (reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        ) + f'#comment_{self.object.id}')


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    raise_exception = False

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        """Перенаправляем на страницу поста при отсутствии прав."""
        comment = self.get_object()
        return redirect('blog:post_detail', post_id=comment.post.id)

    def get_success_url(self):
        return (reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.id}
        ) + f'#comment_{self.object.id}')


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.id}
        )
