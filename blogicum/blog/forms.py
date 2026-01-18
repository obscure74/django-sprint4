"""Формы для приложения blog."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Category, Comment, Location, Post


class RegistrationForm(UserCreationForm):
    """Форма регистрации."""

    email = forms.EmailField(
        required=True,
        label='Адрес электронной почты'
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,  # Обязательное!
        label='Имя',
        help_text='Обязательное поле'
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,  # Обязательное!
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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email уже используется')
        return email

    def save(self, commit=True):
        """Сохраняем пользователя, гарантируя что имя заполнено."""
        user = super().save(commit=False)
        # Гарантируем что first_name не пустое
        if not user.first_name or not user.first_name.strip():
            user.first_name = user.username
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    """Редактирование профиля."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
        """Настройка формы."""
        super().__init__(*args, **kwargs)
        # Делаем email обязательным
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

    def __init__(self, *args, **kwargs):
        """Настройка формы."""
        super().__init__(*args, **kwargs)
        # Убедитесь что queryset существует
        if 'category' in self.fields:
            self.fields['category'].queryset = Category.objects.filter(
                is_published=True
            )
        if 'location' in self.fields:
            self.fields['location'].queryset = Location.objects.filter(
                is_published=True
            )

        # Фильтруем местоположения
        if 'location' in self.fields:
            self.fields['location'].queryset = Location.objects.filter(
                is_published=True
            )
            self.fields['location'].widget.attrs.update(
                {'class': 'form-control'}
            )

        # Поле is_published
        if 'is_published' in self.fields:
            self.fields['is_published'].widget.attrs.update(
                {'class': 'form-check-input'}
            )


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
