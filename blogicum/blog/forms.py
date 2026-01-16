"""Формы для работы с публикациями."""
from django import forms
from django.contrib.auth.models import User
from .models import Post, Category, Comment


class UserEditForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования публикации."""

    class Meta:
        model = Post
        fields = (
            'title', 'text', 'pub_date',
            'location', 'category', 'image'
        )
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'text': forms.Textarea(attrs={'rows': 10}),
        }
        help_texts = {
            'pub_date': (
                'Если установить дату и время в будущем — '
                'можно делать отложенные публикации'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем только опубликованные категории
        self.fields['category'].queryset = Category.objects.filter(
            is_published=True
        )


class CommentForm(forms.ModelForm):
    """Форма для добавления и редактирования комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Введите ваш комментарий...'
            }),
        }
        labels = {
            'text': 'Текст комментария',
        }
