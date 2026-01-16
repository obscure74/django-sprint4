from blog.models import Post
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CreationForm

User = get_user_model()


def signup(request):
    """
    Страница регистрации нового пользователя.

    Context:
        form: Форма регистрации
    """
    if request.method == 'POST':
        form = CreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Регистрация прошла успешно! Теперь вы можете войти.'
            )
            return redirect('auth:login')
    else:
        form = CreationForm()

    return render(request, 'users/signup.html', {'form': form})


def profile(request, username):
    """
    Страница профиля пользователя.

    Выводит информацию о пользователе и его публикации с пагинацией.

    Args:
        username: Имя пользователя

    Context:
        profile_user: Объект пользователя
        page_obj: Объект страницы с постами
        is_owner: Флаг, является ли текущий пользователь владельцем профиля
    """
    user = get_object_or_404(User, username=username)

    # Получаем посты пользователя
    post_list = Post.objects.select_related(
        'category', 'location'
    ).filter(
        author=user
    ).order_by('-pub_date')

    # Для не-авторов показываем только опубликованные посты
    if request.user != user:
        post_list = post_list.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    # Аннотируем количество комментариев
    post_list = post_list.annotate(comment_count=Count('comments'))

    # Пагинация: 10 постов на странице
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'is_owner': request.user == user,
    }

    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    """
    Редактирование профиля пользователя.

    Доступно только залогиненному пользователю для своего профиля.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('users:profile', username=request.user.username)
    else:
        form = PasswordChangeForm(request.user)

    context = {'form': form}
    return render(request, 'users/edit_profile.html', context)
