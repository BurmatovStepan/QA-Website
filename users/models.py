from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Count, Q, QuerySet, UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils import timezone

from common.base_models import TimeStampedModel
from common.constants import (BEST_MEMBERS_FETCH_LIMIT,
                              RECENT_ACTIVITES_FETCH_LIMIT)
from users.constants import (MAX_USER_DISPLAY_NAME_LENGTH,
                             MAX_USER_LOGIN_LENGTH, MIN_USER_LOGIN_LENGTH)

if TYPE_CHECKING:
    from qa.models import Answer, Question


class CustomUserManager(BaseUserManager):
    def create_user(self, login: str, email: str, password: str | None = None, **extra_fields) -> CustomUser:
        if not login:
            raise ValueError("The Login field must be set")

        email = self.normalize_email(email)
        user = self.model(login=login, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, login: str, email: str, password: str, **extra_fields) -> CustomUser:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(login, email, password, **extra_fields)

    def get_best_members(self, count: int = BEST_MEMBERS_FETCH_LIMIT) -> QuerySet[CustomUser]:
        return self.order_by("-rating")[:count]

    def get_user_detail(self) -> QuerySet[CustomUser]:
        return (
            self.all()
            .annotate(
                total_questions_asked=Count("questions", distinct=True),
                total_answers_posted=Count("answers", distinct=True)
            )
        )
    

class CustomUser(TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    objects: CustomUserManager = CustomUserManager()

    login = models.CharField(max_length=MAX_USER_LOGIN_LENGTH, unique=True, validators=[MinLengthValidator(MIN_USER_LOGIN_LENGTH)])
    email = models.EmailField(unique=True)

    display_name = models.CharField(max_length=MAX_USER_DISPLAY_NAME_LENGTH, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    rating = models.IntegerField(default=0)

    page_size_preference = models.IntegerField(default=None, blank=True, null=True)

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

    def __str__(self) -> str:
        return self.display_name if self.display_name else self.login


class ActivityManager(models.Manager):
    def get_recent_activities(self, user, count: int = RECENT_ACTIVITES_FETCH_LIMIT):
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
        "Q_RECEIVED_LIKE": ("received a like on question: \"{title}\"", "question_discussion"),
        "Q_RECEIVED_ANSWER": ("received an answer to question: \"{title}\"", "question_discussion"),
        "A_RECEIVED_LIKE": ("received a like on answer to \"{title}\"", "question_discussion"),
        "A_MARKED_CORRECT": ("had an answer marked correct to \"{title}\"", "question_discussion"),
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

    def __str__(self) -> str:
        return f"{self.user} - {self.type}"

    def get_display_info(self, page_size: int) -> dict[str, str]:
        title = ""
        link_kwargs = {}
        page_query = ""
        fragment = ""

        template, url = self._DISPLAY_MAP[self.type]

        if self.type.startswith("Q_"):
            question: Question = self.target
            title = question.title
            link_kwargs = {"id": question.id, "slug": question.slug}

        if self.type.startswith("A_"):
            answer: Answer = self.target
            question = answer.question
            title = question.title
            link_kwargs = {"id": question.id, "slug": question.slug}

            answers = (
                question.answers
                .filter(is_active=True)
                .order_by("-is_correct", "-rating_total")
            )

            precedence_filter = (
                Q(is_correct__gt=answer.is_correct) |

                Q(is_correct=answer.is_correct) &
                Q(rating_total__gt=answer.rating_total) |

                Q(is_correct=answer.is_correct) &
                Q(rating_total=answer.rating_total) &
                Q(id__lt=answer.id)
            )

            preceding_answers_count = answers.filter(precedence_filter).count()
            page_number = preceding_answers_count // page_size + 1

            page_query = f"?page={page_number}"
            fragment = f"#{answer.id}"

        if self.type.startswith("U_"):
            user: CustomUser = self.target
            link_kwargs = {"id": user.id}

        description = template.format(title=title)
        link_url = reverse(url, kwargs=link_kwargs) + page_query + fragment

        return {
            "description": description,
            "link_url": link_url
        }
