from typing import Any

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Q
from django.http import HttpRequest

from users.models import CustomUser


class LoginEmailBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, username: str | None = None, password: str | None = None, **kwargs: Any) -> AbstractBaseUser | None:
        try:
            user = CustomUser.objects.get(Q(login__iexact=username) | Q(email__iexact=username))
        except CustomUser.DoesNotExist:
            return None

        if user.check_password(password) and user.is_active:
            return user

        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None
