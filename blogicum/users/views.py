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
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/registration_form.html', {'form': form})


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
        'profile_user': profile_user,
        'page_obj': page_obj,
    })


@login_required
def edit_profile(request, username):
    """Редактирование профиля."""
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect('profile', username=username)
    return render(request, 'blog/edit_profile.html', {'user': user})


@login_required
def change_password(request, username):
    """Смена пароля."""
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect('profile', username=username)
    return render(request, 'blog/change_password.html', {'user': user})
