from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования публикаций."""

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'text': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы с настройкой формата даты."""
        super().__init__(*args, **kwargs)
        self.fields['pub_date'].input_formats = ['%Y-%m-%dT%H:%M']


class CommentForm(forms.ModelForm):
    """Форма для создания и редактирования комментариев."""

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Оставьте ваш комментарий...'
            }),
        }
        labels = {
            'text': '',
        }
