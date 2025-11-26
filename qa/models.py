from __future__ import annotations

from datetime import timedelta

from django.db import models
from django.db.models import Q, QuerySet, Sum, UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone
from django.utils.text import slugify

from common.base_models import TimeStampedModel
from common.constants import POPULAR_TAGS_FETCH_LIMIT
from users.models import CustomUser

MAX_TAG_NAME_LENGTH = 50

MAX_QUESTION_TITLE_LENGTH = 100
MAX_QUESTION_CONTENT_LENGTH = 4000

MAX_ANSWER_PREVIEW_LENGTH = 20

LIKE = 1
DISLIKE = -1
VOTE_CHOICES = [
    (LIKE, "Like"),
    (DISLIKE, "Dislike"),
]


class TagManager(models.Manager):
    def get_popular_tags(self, count: int = POPULAR_TAGS_FETCH_LIMIT) -> QuerySet[Tag]:
        return self.annotate(
            rating_total=Sum("questions__rating_total", default=0)
            ).order_by("-rating_total")[:count]


class Tag(models.Model):
    objects: TagManager = TagManager()

    name = models.CharField(max_length=MAX_TAG_NAME_LENGTH, unique=True)
    slug = models.SlugField(max_length=MAX_TAG_NAME_LENGTH, unique=True)

    constraints = [
        UniqueConstraint(Lower("name"), name="tag_name_case_insensitive_unique"),
    ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class QuestionManager(models.Manager):
    def get_question_list(self, search_query="") -> QuerySet[Question]:
        queryset = (
            self.all()
            .filter(is_active=True)
            .select_related("author")
            .prefetch_related("tags")
            .order_by("-created_at")
        )
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

        return queryset

    def exclude_disliked_by_user(self, queryset: QuerySet[Question], user: CustomUser | None) -> QuerySet[Question]:
        if user is None:
            return queryset

        disliked_question_ids = (
            user.question_votes
            .filter(type=DISLIKE)
            .values_list("question_id", flat=True)
        )

        sort_last = models.Case(
            models.When(id__in=disliked_question_ids, then=models.Value(1)),
            default=models.Value(0),
        )

        return (
            queryset
            .annotate(sort_last=sort_last)
            .order_by("sort_last", "-created_at")
        )

    def get_discussion_detail(self) -> QuerySet[Question]:
        return (
            self.filter(is_active=True)
            .select_related("author")
            .prefetch_related("tags")
        )

    def get_hot_questions(self, queryset: QuerySet[Question], lookback_period: int, user: CustomUser | None):
        # TODO Probably remove because too hard
        lookback_period_ago = timezone.now() - timedelta(days=lookback_period)

        if user is not None:
            queryset = Question.objects.exclude_disliked_by_user(queryset, user)
            return queryset.order_by("sort_last", "-rating_total", "-created_at")

        return queryset.order_by("-rating_total", "-created_at")

# TODO Add views and timestamp to question-card
class Question(TimeStampedModel):
    objects: QuestionManager = QuestionManager()

    slug = models.SlugField(max_length=100, unique=True)
    author = models.ForeignKey(to=CustomUser, on_delete=models.SET_NULL, related_name="questions", null=True)

    view_count = models.IntegerField(default=0)
    rating_total = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)

    tags = models.ManyToManyField(to=Tag, related_name="questions")

    title = models.CharField(max_length=MAX_QUESTION_TITLE_LENGTH)
    content = models.TextField(max_length=MAX_QUESTION_CONTENT_LENGTH)

    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self) -> str:
        return self.title


# TODO Add timestamp to answer-card
class Answer(TimeStampedModel):
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE, related_name="answers")
    author = models.ForeignKey(to=CustomUser, on_delete=models.SET_NULL, related_name="answers", null=True)
    rating_total = models.IntegerField(default=0)

    content = models.TextField(max_length=4000)
    is_correct = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        if self.author is None:
            return f"{self.content if len(self.content) <= MAX_ANSWER_PREVIEW_LENGTH else self.content[:MAX_ANSWER_PREVIEW_LENGTH] + '...'}"

        return f"{self.content if len(self.content) <= MAX_ANSWER_PREVIEW_LENGTH else self.content[:MAX_ANSWER_PREVIEW_LENGTH] + '...'}"


class QuestionVote(TimeStampedModel):
    type = models.SmallIntegerField(choices=VOTE_CHOICES)

    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name="question_votes")
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE, related_name="votes")

    class Meta:
        verbose_name = "Оценка к вопросу"
        verbose_name_plural = "Оценки к вопросу"

        constraints = [
            UniqueConstraint(
                fields=["user", "question"],
                name="unique_user_question_vote"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} {'liked' if self.type == 1 else 'disliked'} {self.question}"


class AnswerVote(TimeStampedModel):
    type = models.SmallIntegerField(choices=VOTE_CHOICES)

    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name="answer_votes")
    answer = models.ForeignKey(to=Answer, on_delete=models.CASCADE, related_name="votes")

    class Meta:
        verbose_name = "Оценка к ответу"
        verbose_name_plural = "Оценки к ответу"

        constraints = [
            UniqueConstraint(
                fields=["user", "answer"],
                name="unique_user_answer_vote"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} {'liked' if self.type == 1 else 'disliked'} {self.answer}"
