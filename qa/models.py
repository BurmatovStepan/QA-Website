from django.db import models
from users.models import CustomUser
from django.db.models import Count
from django.utils import timezone


class QuestionManager(models.Manager):
    def with_answer_count(self):
        return self.annotate(answer_count=Count("answer"))


class Question(models.Model):
    objects = QuestionManager()

    slug = models.CharField(max_length=120)
    author = models.ForeignKey(to=CustomUser, on_delete=models.SET_NULL)
    rating = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    title = models.CharField(max_length=120)
    content = models.TextField(max_length=4000)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.title
