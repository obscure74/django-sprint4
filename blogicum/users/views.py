"""Представления для работы с пользователями."""
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

User = get_user_model()


def registration(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('blog:index')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/registration_form.html', {'form': form})


def profile(request, username):
    """Страница профиля пользователя."""
    profile_user = get_object_or_404(User, username=username)

    # Для автора показываем все посты
    if request.user == profile_user:
        post_list = profile_user.posts.all()
    else:
        # Для других пользователей - только опубликованные
        post_list = profile_user.posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    # Аннотация для количества комментариев
    post_list = post_list.annotate(
        comment_count=Count('comments')
    ).select_related(
        'category', 'location'
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request, username):
    """
    Редактирование профиля пользователя.
    """
    user = get_object_or_404(User, username=username)

    if request.user != user:
        return redirect('users:profile', username=username)

    # Реализация редактирования профиля
    return render(request, 'users/edit_profile.html', {'user': user})


@login_required
def change_password(request, username):
    """
    Изменение пароля пользователя.
    """
    user = get_object_or_404(User, username=username)

    if request.user != user:
        return redirect('users:profile', username=username)

    # Реализация смены пароля
    return render(request, 'users/change_password.html', {'user': user})