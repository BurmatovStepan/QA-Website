from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone

from common.base_models import TimeStampedModel


class CustomUserManager(BaseUserManager):
    def create_user(self, login, email, password=None, **extra_fields):
        if not login:
            raise ValueError("The Login field must be set")

        email = self.normalize_email(email)
        user = self.model(login=login, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, login, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(login, email, password, **extra_fields)


class CustomUser(TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    objects: CustomUserManager = CustomUserManager()

    login = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    display_name = models.CharField(max_length=150, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    rating = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    USERNAME_FIELD = "login"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

        constraints = [
            UniqueConstraint(Lower("login"), name="login_case_insensitive_unique"),
            UniqueConstraint(Lower("email"), name="email_case_insensitive_unique"),
        ]

    def __str__(self):
        return self.login


class Activity(models.Model):
    ACTIVITY_TYPES = [
        ("Q_RECEIVED_LIKE", "Question received a like"),
        ("Q_RECEIVED_ANSWER", "Question received an answer"),
        ("A_RECEIVED_LIKE", "Answer received a like"),
        ("A_MARKED_CORRECT", "Answer was marked correct"),
        ("U_CHANGED_AVATAR", "Changed avatar"),
        ("U_CHANGED_NAME", "Changed name"),
    ]

    type = models.CharField(choices=ACTIVITY_TYPES)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name="activities")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Действие"
        verbose_name_plural = "Действия"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.type}"
