from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Введите адрес электронной почты")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {
            'username': 'Введите логин',
            'password1': 'Введите пароль',
            'password2': 'Введите пароль повторно',
        }

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
