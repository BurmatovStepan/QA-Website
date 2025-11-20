from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count, UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse
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

    # TODO Remove magic numbers
    def get_best_members(self, count=5):
        return self.select_related("profile").order_by("-profile__rating")[:count]

    def get_user_detail(self):
        return (
            self.all()
            .prefetch_related("questions")
            .prefetch_related("answers")
            .annotate(
                total_questions_asked=Count("questions", distinct=True),
                total_answers_posted=Count("answers", distinct=True)
            )
        )



class CustomUser(TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    objects: CustomUserManager = CustomUserManager()

    login = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

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

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")

    display_name = models.CharField(max_length=150, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    rating = models.IntegerField(default=0)

    page_size_preference = models.IntegerField(default=None, blank=True, null=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.display_name if self.display_name else self.user.login


class ActivityManager(models.Manager):
    def get_recent_activities(self, user, count=10):
        return (
            self.all()
            .filter(user=user)
            .prefetch_related(
                "target",
            )
            .order_by("-created_at")[:count]
        )


class Activity(models.Model):
    objects: ActivityManager = ActivityManager()
    ACTIVITY_TYPES = [
        ("Q_RECEIVED_LIKE", "Question received a like"),
        ("Q_RECEIVED_ANSWER", "Question received an answer"),
        ("A_RECEIVED_LIKE", "Answer received a like"),
        ("A_MARKED_CORRECT", "Answer was marked correct"),
        ("U_CHANGED_AVATAR", "Changed avatar"),
        ("U_CHANGED_NAME", "Changed name"),
    ]

    _DISPLAY_MAP = {
        "Q_RECEIVED_LIKE": ("received a like on question: {title}", "question_discussion"),
        "Q_RECEIVED_ANSWER": ("received an answer on question: {title}", "question_discussion"),
        "A_RECEIVED_LIKE": ("received a like on answer to {title}", "question_discussion"),
        "A_MARKED_CORRECT": ("had an answer marked correct on {title}", "question_discussion"),
        "U_CHANGED_AVATAR": ("changed their avatar", "profile"),
        "U_CHANGED_NAME": ("changed their display name", "profile"),
    }

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

    def get_display_info(self):
        title = ""
        link_kwargs = {}
        fragment = ""

        template, url = self._DISPLAY_MAP[self.type]
        target_object = self.target

        if self.type.startswith("Q_"):
            title = target_object.title
            link_kwargs = {"id": target_object.id, "slug": target_object.slug}

        if self.type.startswith("A_"):
            question = target_object.question
            title = question.title
            link_kwargs = {"id": question.id, "slug": question.slug}

            # TODO Fix incorrect linking to answers not on the first page
            #? (but they are correct why aren't they on the first page)
            if self.type == "A_MARKED_CORRECT":
                fragment = f"#{target_object.id}"

        if self.type.startswith("U_"):
            link_kwargs = {"id": target_object.id}

        description = template.format(title=title)
        link_url = reverse(url, kwargs=link_kwargs) + fragment

        return {
            "description": description,
            "link_url": link_url
        }
