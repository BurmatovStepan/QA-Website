from typing import Any

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import Http404
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, TemplateView

from common.mixins import (MOCK_ACTIVITIES, MOCK_ANSWERS, MOCK_QUESTIONS,
                           MOCK_USERS, BaseContextViewMixin)
from common.utils import get_author_info

DEFAULT_PAGINATION_SIZE = 10

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
        mock_questions_with_author = MOCK_QUESTIONS[:]
        for question in mock_questions_with_author:
            question["author"] = get_author_info(question["id"])

        if (self.current_user is not None):
            disliked_ids = self.current_user.get("disliked_questions", [])
            mock_questions_with_author.sort(key=lambda question: question["id"] in disliked_ids)

        return mock_questions_with_author


class QuestionDiscussionView(BaseContextViewMixin, DetailView):
    template_name = "question-discussion.html"
    context_object_name = "question"

    def get_queryset(self):
        return MOCK_QUESTIONS

    def get_object(self, queryset: QuerySet[Any] | None=None):
        if queryset is None:
            queryset = self.get_queryset()

        question_id = self.kwargs.get("id")
        found_question = next(
            (question for question in MOCK_QUESTIONS if question.get("id") == question_id),
            None
        )
        if (found_question is None):
            raise Http404(f"Question with ID '{question_id}' does not exist.")

        found_question["author"] = get_author_info(question_id)
        return found_question

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        question = context["question"]

        context["page_title"] = f"Question | {question.get("title")}"

        found_answers = [
            answer for answer in MOCK_ANSWERS if answer.get("question_id") == question.get("id")
        ]

        found_answers_with_author = found_answers[:]
        for answer in found_answers_with_author:
            answer["author"] = get_author_info(answer["author_id"])

        paginator = Paginator(found_answers_with_author, self.items_per_page or DEFAULT_PAGINATION_SIZE)

        page_number = self.request.GET.get("page")
        answer_page_object = paginator.get_page(page_number)

        context["page_obj"] = answer_page_object
        context["paginator"] = paginator
        context["mock_answers"] = answer_page_object.object_list

        return context


class QuestionListingView(BaseContextViewMixin, ListView):
    template_name = "question-listing.html"
    page_title = "Question Listing"

    paginate_by = DEFAULT_PAGINATION_SIZE
    context_object_name = "mock_questions"

    def get(self, request, *args, **kwargs):
        self.paginate_by = self.items_per_page or self.paginate_by
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        search_query = self.request.GET.get("query", "").lower()
        tag = self.request.GET.get("tag", "").lower()
        hot_period = self.request.GET.get("hot", None)

        filtered_mock_questions = []
        for question in MOCK_QUESTIONS:
            if (search_query not in question.get("title").lower()):
                continue

            tags_lowercase = [tag.lower() for tag in question.get("tags")]
            if (tag and tag not in tags_lowercase):
                continue

            if (hot_period and not question.get("is_hot")):
                continue

            filtered_mock_questions.append(question)

        mock_questions_with_author = filtered_mock_questions
        for question in mock_questions_with_author:
            question["author"] = get_author_info(question["id"])

        if (self.current_user is not None):
            disliked_ids = self.current_user.get("disliked_questions", [])
            mock_questions_with_author.sort(key=lambda question: question["id"] in disliked_ids)

        return mock_questions_with_author


    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get("query", "")
        tag = self.request.GET.get("tag", "")
        hot_period = self.request.GET.get("hot", None)

        if (search_query):
            context["main_title"] = "Search: "
            context["main_title_extra"] = search_query[:20]
        elif (tag):
            context["main_title"] = "Tag: "
            context["main_title_extra"] = tag
        elif (hot_period):
            context["main_title"] = "Hot: "
            context["main_title_extra"] = f"last {hot_period} days"
        else:
            context["main_title"] = "Latest questions"
            context["main_title_extra"] = None

        return context


class NewQuestionView(BaseContextViewMixin, TemplateView):
    template_name = "new-question.html"
    page_title = "New Question"
    main_title = "New Question"
