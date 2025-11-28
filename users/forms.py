from typing import Any

from django import forms

from users.constants import (MAX_AVATAR_SIZE, MAX_USER_DISPLAY_NAME_LENGTH,
                             MAX_USER_LOGIN_LENGTH, MIN_PASSWORD_LENGHT,
                             MIN_USER_LOGIN_LENGTH)
from users.models import CustomUser


class LoginForm(forms.Form):
    login = forms.CharField(
        label="Login/Email",
        max_length=MAX_USER_LOGIN_LENGTH,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter login or email",
            "autocomplete": "username"
        })
    )

    password = forms.CharField(
        label="Password",
        min_length=MIN_PASSWORD_LENGHT,
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter password",
            "autocomplete": "current-password"
        })
    )


class RegisterForm(forms.Form):
    login = forms.CharField(
        label="Login",
        min_length=MIN_USER_LOGIN_LENGTH,
        max_length=MAX_USER_LOGIN_LENGTH,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter login",
            "autocomplete": "username"
        })
    )

    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "example@google.com",
            "autocomplete": "email"
        })
    )

    display_name = forms.CharField(
        label="Displayed name",
        max_length=MAX_USER_DISPLAY_NAME_LENGTH,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter display name"
        })
    )

    password = forms.CharField(
        label="Password",
        min_length=MIN_PASSWORD_LENGHT,
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter password",
            "autocomplete": "current-password"
        })
    )

    repeat_password = forms.CharField(
        label="Repeat password",
        min_length=MIN_PASSWORD_LENGHT,
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Repeat password",
            "autocomplete": "current-password"
        })
    )

    avatar = forms.ImageField(
        label="Upload avatar",
        required=False,
        widget=forms.FileInput(attrs={
            "accept": "image/*"
        })
    )

    def clean_login(self):
        login = self.cleaned_data.get("login")
        if CustomUser.objects.filter(login__iexact=login).exists():
            raise forms.ValidationError("This login is already taken. Please choose another.")

        return login

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")

        return email

    def clean_avatar(self):
        uploaded_file = self.cleaned_data.get("avatar")

        if uploaded_file:
            if uploaded_file.size > MAX_AVATAR_SIZE:
                max_mb_size = MAX_AVATAR_SIZE / 1024 / 1024
                raise forms.ValidationError(
                    f"The file size ({uploaded_file.size / 1024 / 1024:.2f}MB) exceeds the maximum limit of {max_mb_size:.0f}MB."
                )

        return uploaded_file

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        errors = {}

        password = cleaned_data.get("password")
        repeat_password = cleaned_data.get("repeat_password")

        if password is not None and repeat_password is not None:
            if password != repeat_password:
                errors["repeat_password"] = "Пароли не совпадают"

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data
