"""Представления для приложения blog."""
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.http import HttpResponseNotFound
from django.http import HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import UpdateView


from .forms import CommentForm
from .forms import PostForm
from .forms import RegistrationForm
from .forms import UserEditForm
from .models import Category
from .models import Comment
from .models import Post

User = get_user_model()


def registration(request):
    """Регистрация пользователя (FBV версия)."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(
        request, 'registration/registration_form.html', {
            'form': form,
        }
    )


def csrf_failure(request, reason=''):
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

    if ((not post.is_published or not post.category.is_published
         or post.pub_date > timezone.now())
            and request.user != post.author):
        raise Http404("Пост не найден")

    comments = post.comments.select_related('author').all()
    form = CommentForm() if request.user.is_authenticated else None

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


@login_required
def profile_view(request, username):
    """Профиль пользователя."""
    user = get_object_or_404(User, username=username)

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

    post_list = post_list.annotate(comment_count=Count('comments'))
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/profile.html', {
        'profile': user,
        'page_obj': page_obj,
    })


@login_required
def edit_profile(request, username):
    """Редактирование профиля (FBV версия)."""

    user = get_object_or_404(User, username=username)

    if request.user != user:
        return redirect('blog:profile', username=username)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('blog:profile', username=username)
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
    """Редактирование профиля."""

    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
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

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

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

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

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
