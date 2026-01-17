"""Представления для работы с пользователями."""
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from blog.models import Post

User = get_user_model()


def registration(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Регистрация прошла успешно!'
            )
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/registration_form.html', {'form': form})


def profile(request, username):
    """Страница профиля пользователя."""
    # Получаем пользователя или 404
    profile_user = get_object_or_404(User, username=username)
    
    # Определяем, какие посты показывать
    if request.user == profile_user:
        # Автор видит все свои посты
        post_list = Post.objects.filter(author=profile_user)
    else:
        # Другие видят только опубликованные
        post_list = Post.objects.filter(
            author=profile_user,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    
    # Аннотируем количество комментариев
    post_list = post_list.annotate(
        comment_count=Count('comments')
    ).select_related('category', 'location').order_by('-pub_date')
    
    # Пагинация
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
    """Редактирование профиля."""
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect('profile', username=username)
    # Заглушка - реализуйте по необходимости
    return render(request, 'users/edit_profile.html', {'user': user})


@login_required
def change_password(request, username):
    """Смена пароля."""
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect('profile', username=username)
    # Заглушка - реализуйте по необходимости
    return render(request, 'users/change_password.html', {'user': user})