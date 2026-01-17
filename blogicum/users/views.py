"""Представления для работы с пользователями."""
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone

from .forms import UserRegistrationForm

User = get_user_model()


def registration(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Регистрация прошла успешно! Теперь вы можете войти.'
            )
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/registration.html', {'form': form})


@login_required
def profile(request, username):
    """Страница профиля пользователя."""
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        post_list = profile_user.posts.all()
    else:
        post_list = profile_user.posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    post_list = post_list.annotate(comment_count=Count('comments'))

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'users/profile.html', context)
