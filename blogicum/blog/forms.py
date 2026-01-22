"""Формы для приложения blog."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .constants import (DATETIME_FORMAT_HTML, FIRST_NAME_MAX_LENGTH,
                        LAST_NAME_MAX_LENGTH)
from .models import Comment, Post


class RegistrationForm(UserCreationForm):
    """Форма регистрации."""

    email = forms.EmailField(
        required=True,
        label='Адрес электронной почты'
    )
    first_name = forms.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        required=True,
        label='Имя',
        help_text='Обязательное поле'
    )
    last_name = forms.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        required=True,
        label='Фамилия',
        help_text='Обязательное поле'
    )

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

    def clean_first_name(self):
        """Проверяем что имя заполнено."""
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise forms.ValidationError('Имя обязательно для заполнения')
        return first_name

    def clean_last_name(self):
        """Проверяем что фамилия заполнена."""
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name:
            raise forms.ValidationError('Фамилия обязательна для заполнения')
        return last_name

    def clean_email(self):
        """Проверяем уникальность email."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email уже используется')
        return email


class UserEditForm(forms.ModelForm):
    """Редактирование профиля."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
        """Настройка формы."""
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        """Проверяем уникальность email."""
        email = self.cleaned_data.get('email')
        if (User.objects.filter(email=email)
                .exclude(id=self.instance.id)
                .exists()):
            raise ValidationError(
                'Этот email уже используется другим пользователем.'
            )
        return email

    def clean_first_name(self):
        """Проверяем что имя заполнено."""
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise ValidationError('Имя обязательно для заполнения')
        return first_name

    def clean_last_name(self):
        """Проверяет что фамилия заполнена."""
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name:
            raise ValidationError('Фамилия обязательна для заполнения')
        return last_name


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
                format=DATETIME_FORMAT_HTML,
                attrs={'type': 'datetime-local'}
            ),
        }

    def __init__(self, *args, **kwargs):
        """Настройка формы."""
        super().__init__(*args, **kwargs)
        if 'category' in self.fields:
            self.fields['category'].queryset = self.fields[
                'category'
            ].queryset.filter(is_published=True)
        if 'location' in self.fields:
            self.fields['location'].queryset = self.fields[
                'location'
            ].queryset.filter(is_published=True)


class CommentForm(forms.ModelForm):
    """Форма комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Введите ваш комментарий...'
            }),
        }
        labels = {
            'text': 'Текст комментария',
        }
