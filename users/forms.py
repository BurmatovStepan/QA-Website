from django import forms

MAX_LOGIN_LENGTH = 150
MIN_PASSWORD_LENGHT = 8


class LoginForm(forms.Form):
    login = forms.CharField(
        max_length=MAX_LOGIN_LENGTH,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter login"
        })
    )

    password = forms.CharField(
        min_length=MIN_PASSWORD_LENGHT,
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter password"
        })
    )
