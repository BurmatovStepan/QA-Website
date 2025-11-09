import copy
from typing import Any

from django.core.paginator import Paginator
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import Http404
from django.http.response import HttpResponse as HttpResponse
from django.views.generic import DetailView, ListView, TemplateView

from common.mixins import (MOCK_ANSWERS, MOCK_QUESTIONS, MOCK_USERS,
                           BaseContextViewMixin)

DEFAULT_PAGINATION_SIZE = 10
DEFAULT_HOT_QUESTIONS_LOOKBACK_DAYS = 3
TAG_DELIMITER = "~"

class HomepageView(BaseContextViewMixin, ListView):
    template_name = "index.html"
    page_title = "AskMe"
    main_title = "New Questions"
    main_title_extra = "Hot Questions"

    paginate_by = DEFAULT_PAGINATION_SIZE
    context_object_name = "mock_questions"

    def get(self, request, *args, **kwargs):
        self.paginate_by = self.items_per_page or self.paginate_by
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        search_query = self.request.GET.get("query", "").lower()

        questions = [
            copy.deepcopy(question) for question in MOCK_QUESTIONS.values()
            if search_query in question["title"].lower()
        ]

        for question in questions:
            question["author"] = MOCK_USERS.get(question["author_id"])

        if (self.current_user is not None):
            disliked_ids = self.current_user["disliked_questions"]
            questions.sort(key=lambda question: question["id"] in disliked_ids)

        return questions


class QuestionDiscussionView(BaseContextViewMixin, DetailView):
    template_name = "question-discussion.html"
    context_object_name = "question"

    def get_queryset(self):
        return MOCK_QUESTIONS

    def get_object(self, queryset: QuerySet[Any] | None=None):
        if queryset is None:
            queryset = self.get_queryset()

        question_id = self.kwargs.get("id")
        question = queryset.get(question_id)

        if (question is None):
            raise Http404(f"Question with ID '{question_id}' does not exist.")

        question["author"] = MOCK_USERS.get(question["author_id"])
        return question

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        question = context["question"]

        context["page_title"] = f"Question | {question["title"]}"

        found_answers = [
            copy.deepcopy(answer) for answer in MOCK_ANSWERS.values() if answer["question_id"] == question["id"]
        ]

        for answer in found_answers:
            answer["author"] = MOCK_USERS.get(answer["author_id"])

        paginator = Paginator(found_answers, self.items_per_page or DEFAULT_PAGINATION_SIZE)

        page_number = self.request.GET.get("page")
        answer_page_object = paginator.get_page(page_number)

        context["page_obj"] = answer_page_object
        context["paginator"] = paginator
        context["mock_answers"] = answer_page_object.object_list

        return context


class HotQuestionsView(BaseContextViewMixin, ListView):
    template_name = "question-listing.html"
    page_title = "Hot Questions"
    main_title = "Hot: "

    paginate_by = DEFAULT_PAGINATION_SIZE
    context_object_name = "mock_questions"

    hot_period = DEFAULT_HOT_QUESTIONS_LOOKBACK_DAYS

    def get(self, request, *args, **kwargs):
        self.paginate_by = self.items_per_page or self.paginate_by
        self.hot_period = kwargs.get("day_amount") or self.hot_period

        return super().get(request, *args, **kwargs)


    def get_queryset(self) -> QuerySet[Any]:
        search_query = self.request.GET.get("query", "").lower()

        questions = []
        for question in MOCK_QUESTIONS.values():
            if (search_query not in question["title"].lower()):
                continue

            if (self.hot_period and not question["is_hot"]):
                continue

            questions.append(copy.deepcopy(question))

        for question in questions:
            question["author"] = MOCK_USERS.get(question["author_id"])

        if (self.current_user is not None):
            disliked_ids = self.current_user["disliked_questions"]
            questions.sort(key=lambda question: question["id"] in disliked_ids)

        return questions


    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["main_title_extra"] = f"last {self.hot_period} {"day" if self.hot_period == 1 else "days"}"

        return context



class TagsQuestionListingView(BaseContextViewMixin, ListView):
    template_name = "question-listing.html"
    page_title = "Tags Question Listing"

    paginate_by = DEFAULT_PAGINATION_SIZE
    context_object_name = "mock_questions"

    tags = set()

    def get(self, request, *args, **kwargs):
        self.paginate_by = self.items_per_page or self.paginate_by
        self.tags = {tag.strip() for tag in kwargs.get("tags_list").split(TAG_DELIMITER) if tag.strip()}

        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        search_query = self.request.GET.get("query", "").lower()

        questions = []
        for question in MOCK_QUESTIONS.values():
            if (search_query not in question["title"].lower()):
                continue

            question_tags_lowercase = {tag.lower() for tag in question["tags"]}
            if (not self.tags <= question_tags_lowercase):
                continue

            questions.append(copy.deepcopy(question))

        for question in questions:
            question["author"] = MOCK_USERS.get(question["author_id"])

        if (self.current_user is not None):
            disliked_ids = self.current_user["disliked_questions"]
            questions.sort(key=lambda question: question["id"] in disliked_ids)

        return questions


    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["main_title"] = "Tag: " if len(self.tags) == 1 else "Tags: "
        context["main_title_extra"] = ", ".join(self.tags)

        return context


class NewQuestionView(BaseContextViewMixin, TemplateView):
    template_name = "new-question.html"
    page_title = "New Question"
    main_title = "New Question"
