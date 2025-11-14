from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count, Sum, UniqueConstraint
from django.db.models.functions import Lower
from django.utils.text import slugify
from django.db.models.query import QuerySet
from django.db.models import Q
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from common.base_models import TimeStampedModel
from users.models import CustomUser
from django.db.models import Sum, Count, Q, Subquery, OuterRef, Value, IntegerField
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.models import ContentType


class TagManager(models.Manager):
    def get_popular_tags(self, count=10):
        return self.annotate(
            rating_total=Sum("questions__rating_total", default=0)
        ).order_by("-rating_total")[:count]


class Tag(models.Model):
    objects: TagManager = TagManager()

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

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

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def get_question_list(self, search_query=""):
        best_answer_id_subquery = Subquery(
            Answer.objects.filter(
                question=OuterRef("id")
            )
            .order_by("-is_correct", "-rating_total")
            .values("id")[:1],
            output_field=IntegerField()
        )

        queryset = (
            self.all()
            .filter(is_active=True)
            .select_related("author")
            .annotate(
                answer_count=Count("answers", distinct=True),
                best_answer_id=best_answer_id_subquery
            )
            .order_by("-created_at")
        )
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

        return queryset

    def exclude_disliked_by_user(self, queryset, user):
        if user is None:
            return queryset

        question_content_type = ContentType.objects.get_for_model(self.model)

        disliked_question_ids = (
            user.votes
            .filter(
                type=Vote.DISLIKE,
                content_type=question_content_type
            )
            .values_list("object_id", flat=True)
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

    def get_discussion_detail(self):
        return (
            self.filter(is_active=True)
            .select_related("author")
            .prefetch_related("tags")
        )

    def get_hot_questions(self, queryset, lookback_period, user):
        lookback_period_ago = timezone.now() - timedelta(days=lookback_period)

        if user is not None:
            queryset = Question.objects.exclude_disliked_by_user(queryset, user)
            return queryset.order_by("sort_last", "-rating_total", "-created_at")

        return queryset.order_by("-rating_total", "-created_at")


class Question(TimeStampedModel):
    objects: QuestionManager = QuestionManager()

    slug = models.SlugField(max_length=100, unique=True)
    author = models.ForeignKey(to=CustomUser, on_delete=models.SET_NULL, related_name="questions", null=True)
    view_count = models.IntegerField(default=0)
    rating = GenericRelation("Vote", related_query_name="question_votes")
    rating_total = models.IntegerField(default=0)
    tags = models.ManyToManyField(to=Tag, related_name="questions")

    title = models.CharField(max_length=100)
    content = models.TextField(max_length=4000)

    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.title


class AnswerManager(models.Manager):
    ...


class Answer(TimeStampedModel):
    objects: AnswerManager = AnswerManager()

    question = models.ForeignKey(to=Question, on_delete=models.CASCADE, related_name="answers")
    author = models.ForeignKey(to=CustomUser, on_delete=models.SET_NULL, related_name="answers", null=True)
    rating = GenericRelation("Vote", related_query_name="answer_votes")
    rating_total = models.IntegerField(default=0)

    content = models.TextField(max_length=4000)
    is_correct = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        if self.author is None:
            return f"{self.content if len(self.content) <= 20 else self.content[:20] + "..."}"

        return f"{self.content if len(self.content) <= 20 else self.content[:20] + "..."}"


class Vote(TimeStampedModel):
    LIKE = 1
    DISLIKE = -1
    VOTE_CHOICES = [
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
    ]

    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name="votes")
    type = models.SmallIntegerField(choices=VOTE_CHOICES)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"

        constraints = [
            UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="unique_user_vote"
            )
        ]

    def __str__(self):
        return f"{self.user} {"liked" if self.type == 1 else "disliked"} {self.content_type} - {self.target}"
