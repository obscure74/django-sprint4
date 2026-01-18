"""Формы для приложения blog."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Post, Comment


class RegistrationForm(UserCreationForm):
    """Форма регистрации."""

    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(max_length=30, required=False, label='Имя')
    last_name = forms.CharField(max_length=30, required=False, label='Фамилия')

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email уже используется')
        return email


class UserEditForm(forms.ModelForm):
    """Редактирование профиля."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if (User.objects.filter(email=email)
                .exclude(id=self.instance.id)
                .exists()):
            raise ValidationError('Email уже используется')
        return email


class PostForm(forms.ModelForm):
    """Форма поста."""

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'image',
            'location',
            'category',
            'is_published'
        )
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
        }


class CommentForm(forms.ModelForm):
    """Форма комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }
