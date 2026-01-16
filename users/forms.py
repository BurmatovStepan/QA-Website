from typing import Any

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

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


class BaseUserProfileForm(forms.Form):
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

    avatar = forms.ImageField(
        label="Upload avatar",
        required=False,
        widget=forms.FileInput(attrs={
            "accept": "image/*"
        })
    )

    def clean_avatar(self) -> UploadedFile | None:
        uploaded_file: UploadedFile | None = self.cleaned_data.get("avatar")

        if uploaded_file:
            if uploaded_file.size > MAX_AVATAR_SIZE:
                max_mb_size = MAX_AVATAR_SIZE / 1024 / 1024
                raise forms.ValidationError(
                    f"The file size ({uploaded_file.size / 1024 / 1024:.2f}MB) exceeds the maximum limit of {max_mb_size:.0f}MB."
                )

        return uploaded_file


class RegisterForm(BaseUserProfileForm):
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

    def clean_login(self) -> str:
        login: str = self.cleaned_data["login"]

        if CustomUser.objects.filter(login__iexact=login).exists():
            raise forms.ValidationError("This login is already taken. Please choose another.")

        return login

    def clean_email(self) -> str:
        email: str = self.cleaned_data["email"]

        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")

        return email

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        repeat_password = cleaned_data.get("repeat_password")

        if password is not None:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error("password", e)

        if password is not None and repeat_password is not None:
            if password != repeat_password:
                self.add_error("repeat_password", "Пароли не совпадают")

        return cleaned_data

    def save(self) -> CustomUser:
        try:
            with transaction.atomic():
                user_login = self.cleaned_data.get("login")
                user_email = self.cleaned_data.get("email")
                user_password = self.cleaned_data.get("password")
                user_display_name = self.cleaned_data.get("display_name")
                user_avatar = self.cleaned_data.get("avatar")

                new_user = CustomUser.objects.create_user(
                    login=user_login,
                    email=user_email,
                    password=user_password,
                    display_name=user_display_name,
                )

                if user_avatar:
                    new_user.avatar = user_avatar
                    new_user.save()

        except Exception as e:
            print(e)
            raise forms.ValidationError("Произошла ошибка при создании записи пользователя. Повторите попытку ещё раз.")

        return new_user


class SettingsFrom(BaseUserProfileForm):
    clear_avatar = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        self.user: CustomUser = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_login(self) -> str:
        login: str = self.cleaned_data["login"]

        if login.lower() != self.user.login.lower():
            if CustomUser.objects.filter(login__iexact=login).exists():
                raise forms.ValidationError("This login is already taken. Please choose another.")

        return login

    def clean_email(self) -> str:
        email: str = self.cleaned_data["email"]

        if email.lower() != self.user.email.lower():
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("A user with this email already exists.")

        return email

    def save(self) -> None:
        try:
            with transaction.atomic():
                self.user.login = self.cleaned_data["login"]
                self.user.email = self.cleaned_data["email"]
                self.user.display_name = self.cleaned_data.get("display_name")

                new_avatar = self.cleaned_data.get("avatar")
                clear_avatar = self.cleaned_data.get('clear_avatar')

                if clear_avatar:
                    self.user.avatar.delete(save=False)
                    self.user.avatar = None
                elif new_avatar:
                    self.user.avatar = new_avatar

                self.user.save()

        except Exception as e:
            print(e)
            raise forms.ValidationError("Произошла ошибка при изменении записи пользователя. Повторите попытку ещё раз.")
