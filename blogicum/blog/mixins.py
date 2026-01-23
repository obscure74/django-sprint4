"""Миксины для приложения blog."""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse

from .forms import CommentForm
from .models import Comment


class CommentBaseMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Базовый миксин для работы с комментариями."""

    model = Comment
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        comment = self.get_object()
        return redirect('blog:post_detail', post_id=comment.post.id)


class CommentDeleteMixin(CommentBaseMixin):
    """Миксин для удаления комментариев."""

    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.id}
        )


class CommentUpdateMixin(CommentDeleteMixin):
    """Миксин для редактирования комментариев."""

    form_class = CommentForm

    def get_success_url(self):
        """URL для редактирования с якорем на комментарий."""
        return super().get_success_url() + f'#comment_{self.object.id}'
