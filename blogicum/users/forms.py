from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CreationForm(UserCreationForm):
    """
    Форма регистрации нового пользователя.

    Наследует от стандартной формы UserCreationForm.

    Fields:
        first_name: Имя
        last_name: Фамилия
        username: Имя пользователя
        email: Email адрес
        password1: Пароль
        password2: Подтверждение пароля
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем email обязательным
        self.fields['email'].required = True

    def clean_email(self):
        """Проверяет уникальность email."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Пользователь с таким email уже существует.')
        return email
