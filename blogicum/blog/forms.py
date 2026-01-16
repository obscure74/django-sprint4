"""Формы для работы с публикациями."""
from django import forms
from django.utils import timezone
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
            "title",
            "text",
            "pub_date",
            "location",
            "category",
            "image",
        )
        widgets = {
            "pub_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем только опубликованные категории
        self.fields["category"].queryset = Category.objects.filter(
            is_published=True
        )

    def clean_pub_date(self):
        """Валидация даты публикации."""
        pub_date = self.cleaned_data.get("pub_date")
        if pub_date and pub_date < timezone.now():
            raise forms.ValidationError(
                "Дата публикации не может быть в прошлом."
            )
        return pub_date


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
