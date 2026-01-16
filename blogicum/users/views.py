"""Представления для работы с пользователями."""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from .forms import UserRegistrationForm, UserEditForm

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
