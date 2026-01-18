"""Представления для работы с пользователями."""
from blog.models import Post
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

User = get_user_model()


def csrf_failure(request, reason=''):
    """Кастомная страница ошибки 403 CSRF."""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    """Кастомная страница ошибки 404."""
    return HttpResponseNotFound(render(request, 'pages/404.html'))


def server_error(request):
    """Кастомная страница ошибки 500."""
    return HttpResponseServerError(render(request, 'pages/500.html'))


def registration(request):
    """Регистрация нового пользователя."""
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


def profile(request, username):
    """Страница профиля пользователя."""
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        post_list = Post.objects.filter(author=profile_user)
    else:
        post_list = Post.objects.filter(
            author=profile_user,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    post_list = post_list.annotate(
        comment_count=Count('comments')
    ).select_related(
        'category', 'location'
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/profile.html', {
        'profile': profile_user,
        'page_obj': page_obj,
    })


@login_required
def edit_profile(request, username):
    """Редактирование профиля."""
    from .forms import UserEditForm
    user = get_object_or_404(User, username=username)

    if request.user != user:
        return redirect('users:profile', username=username)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile', username=username)
    else:
        form = UserEditForm(instance=user)

    return render(request, 'blog/user.html', {'form': form})
