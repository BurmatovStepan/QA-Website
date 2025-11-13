from random import choice, sample

from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count, Sum, UniqueConstraint
from django.db.models.functions import Lower
from django.utils.text import slugify

from common.base_models import TimeStampedModel
from users.models import CustomUser


class TagManager(models.Manager):
    ...


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
    def get_


class Question(TimeStampedModel):
    objects: QuestionManager = QuestionManager()

    slug = models.SlugField(max_length=100, unique=True)
    author = models.ForeignKey(to=CustomUser, on_delete=models.SET_NULL, related_name="questions", null=True)
    view_count = models.IntegerField(default=0)
    rating = GenericRelation("Vote", related_query_name="question_votes")
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
    def with_rating(self):
        return self.annotate(rating=Sum("rating__type", default=0))


class Answer(TimeStampedModel):
    objects: AnswerManager = AnswerManager()

    question = models.ForeignKey(to=Question, on_delete=models.CASCADE, related_name="answers")
    author = models.ForeignKey(to=CustomUser, on_delete=models.SET_NULL, related_name="answers", null=True)
    rating = GenericRelation("Vote", related_query_name="answer_votes")

    content = models.TextField(max_length=4000)
    is_correct = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        if self.author is None:
            return f"{self.content if len(self.content) <= 20 else self.content[:20] + '...'}"

        return f"{self.content if len(self.content) <= 20 else self.content[:20] + '...'}"


class Vote(TimeStampedModel):
    LIKE = 1
    DISLIKE = -1
    VOTE_CHOICES = [
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
    ]

    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
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
