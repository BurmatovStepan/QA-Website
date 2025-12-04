from django import forms

from qa.constants import (MAX_ANSWER_CONTENT_LENGTH,
                          MAX_QUESTION_CONTENT_LENGTH, MAX_QUESTION_TAG_COUNT,
                          MAX_QUESTION_TITLE_LENGTH, MAX_TAG_NAME_LENGTH,
                          MIN_ANSWER_CONTENT_LENGTH,
                          MIN_QUESTION_CONTENT_LENGTH,
                          MIN_QUESTION_TITLE_LENGTH)


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

    def clean_tags(self):
        errors = []

        tags = self.cleaned_data.get("tags")
        if tags:
            tags = {tag.strip().lower() for tag in tags.split(",")}

            if len(tags) > MAX_QUESTION_TAG_COUNT:
                errors.append(f"Tag count ({len(tags)}) exceeds the maximum limit of {MAX_QUESTION_TAG_COUNT}.")

            longest_tag = max(tags, key=len)
            if len(longest_tag) > MAX_TAG_NAME_LENGTH:
                errors.append(f"Lenght of '{longest_tag[:20]}...' ({len(longest_tag)}) exceeds the maximum limit of {MAX_TAG_NAME_LENGTH}.")

        if errors:
            raise forms.ValidationError(errors)

        return tags


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
