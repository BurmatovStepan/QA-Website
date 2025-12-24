from typing import Any

from django import forms
from django.db import transaction
from django.db.models import F
from django.utils.text import slugify

from qa.constants import (MAX_ANSWER_CONTENT_LENGTH,
                          MAX_QUESTION_CONTENT_LENGTH, MAX_QUESTION_TAG_COUNT,
                          MAX_QUESTION_TITLE_LENGTH, MAX_TAG_NAME_LENGTH,
                          MIN_ANSWER_CONTENT_LENGTH,
                          MIN_QUESTION_CONTENT_LENGTH,
                          MIN_QUESTION_TITLE_LENGTH)
from qa.models import Answer, Question, Tag
from users.models import CustomUser


class NewQuestionForm(forms.Form):
    title = forms.CharField(
        label="Title",
        min_length=MIN_QUESTION_TITLE_LENGTH,
        max_length=MAX_QUESTION_TITLE_LENGTH,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Title of your post"
        })
    )

    content = forms.CharField(
        label="Text",
        min_length=MIN_QUESTION_CONTENT_LENGTH,
        max_length=MAX_QUESTION_CONTENT_LENGTH,
        required=True,
        widget=forms.Textarea(attrs={
            "placeholder": "Your full question here"
        })
    )

    tags = forms.CharField(
        label="Tags",
        max_length=MAX_QUESTION_TITLE_LENGTH,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "some tag, another, third"
        })
    )

    def __init__(self, *args, **kwargs):
        self.author: CustomUser = kwargs.pop("author")
        super().__init__(*args, **kwargs)


    def clean_tags(self) -> set[str] | None:
        tags = self.cleaned_data.get("tags")
        if tags:
            tags = {tag.strip().lower() for tag in tags.split(",")}

            if len(tags) > MAX_QUESTION_TAG_COUNT:
                self.add_error("tags", f"Tag count ({len(tags)}) exceeds the maximum limit of {MAX_QUESTION_TAG_COUNT}.")

            longest_tag = max(tags, key=len)
            if len(longest_tag) > MAX_TAG_NAME_LENGTH:
                self.add_error("tags", f"Lenght of '{longest_tag[:20]}...' ({len(longest_tag)}) exceeds the maximum limit of {MAX_TAG_NAME_LENGTH}.")

        return tags

    def save(self) -> Question:
        try:
            with transaction.atomic():
                question = Question(
                    title=self.cleaned_data.get("title"),
                    content=self.cleaned_data.get("content"),
                    author=self.author
                )
                question.save()

                tag_names = self.cleaned_data.get("tags")

                if tag_names:
                    existing_tag_names = set(Tag.objects.filter(name__in=tag_names).values_list("name", flat=True))
                    new_tags = [Tag(name=name, slug=slugify(name)) for name in (tag_names - existing_tag_names)]

                    Tag.objects.bulk_create(new_tags)
                    tags = Tag.objects.filter(name__in=tag_names)
                    question.tags.set(tags)

        except Exception as e:
            print(e)
            raise forms.ValidationError("Произошла ошибка при создании вопроса. Повторите попытку ещё раз.")

        return question


class AnswerForm(forms.Form):
    content = forms.CharField(
        label="",
        min_length=MIN_ANSWER_CONTENT_LENGTH,
        max_length=MAX_ANSWER_CONTENT_LENGTH,
        required=True,
        widget=forms.Textarea(attrs={
            "placeholder": "Enter your answer here"
        })
    )

    def __init__(self, *args, **kwargs):
        self.question: Question | None = kwargs.pop("question", None)
        self.author: CustomUser | None = kwargs.pop("author", None)
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        if self.question is None:
            self.add_error(None, "Форма инициализированна без вопроса.")

        if self.author is None:
            self.add_error(None, "Форма инициализированна без пользователя.")

        return cleaned_data


    def save(self) -> Answer:
        try:
            answer_content = self.cleaned_data["content"]
            new_answer = Answer(
                question=self.question,
                author=self.author,
                content=answer_content
            )
            new_answer.save()

            self.question.answer_count = F("answer_count") + 1
            self.question.save(update_fields=["answer_count"])

            return new_answer

        except Exception as e:
            print(e)
            raise forms.ValidationError("Произошла ошибка при создании ответа. Повторите попытку ещё раз.")
