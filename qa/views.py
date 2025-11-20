from typing import Any

from django.core.paginator import Paginator
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView

from common.constants import DEFAULT_PAGINATION_SIZE
from common.mixins import BaseContextViewMixin
from qa.models import Question

DEFAULT_HOT_QUESTIONS_LOOKBACK_DAYS = 3
TAG_DELIMITER = "~"

# TODO Decide if you type-hint

class HomepageView(BaseContextViewMixin, ListView):
    template_name = "index.html"
    page_title = "AskMe"
    main_title = "New Questions"
    main_title_extra = "Hot Questions"

    paginate_by = DEFAULT_PAGINATION_SIZE
    context_object_name = "questions"

    def get(self, request, *args, **kwargs):
        self.paginate_by = self.page_size or self.paginate_by
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        search_query = self.request.GET.get("query", "").lower()

        queryset = Question.objects.get_question_list(search_query=search_query)
        queryset = Question.objects.exclude_disliked_by_user(queryset, self.current_user)

        return queryset


class QuestionDiscussionView(BaseContextViewMixin, DetailView):
    template_name = "question-discussion.html"
    context_object_name = "question"

    def get_queryset(self):
        return Question.objects.get_discussion_detail()

    def get_object(self, queryset: QuerySet[Any] | None=None):
        if queryset is None:
            queryset = self.get_queryset()

        question_id = self.kwargs.get("id")
        question = get_object_or_404(queryset, id=question_id)

        url_slug = self.kwargs.get("slug")

        if url_slug is None or url_slug != question.slug:
            canonical_url = reverse(
                "question_discussion",
                 kwargs={"id": question.id, "slug": question.slug}
            )
            redirect(canonical_url, permanent=True)

        return question

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        question = context["question"]

        context["page_title"] = f"Question | {question.title}"

        answers_queryset = (
            question.answers
            .filter(is_active=True)
            .select_related("author")
            .order_by("-is_correct", "-rating_total")
        )

        paginator = Paginator(answers_queryset, self.current_user.profile.page_size_preference or DEFAULT_PAGINATION_SIZE)

        page_number = self.request.GET.get("page")
        answer_page_object = paginator.get_page(page_number)

        context["page_obj"] = answer_page_object
        context["paginator"] = paginator
        context["answers"] = answer_page_object.object_list

        # TODO Check if this work
        question.view_count = question.view_count + 1
        question.save(update_fields=["view_count"])

        return context

# TODO Make this accessible from footer or smth
class HotQuestionsView(BaseContextViewMixin, ListView):
    template_name = "question-listing.html"
    page_title = "Hot Questions"
    main_title = "Hot: "

    paginate_by = DEFAULT_PAGINATION_SIZE
    context_object_name = "questions"

    hot_period = DEFAULT_HOT_QUESTIONS_LOOKBACK_DAYS

    def get(self, request, *args, **kwargs):
        self.paginate_by = self.current_user.profile.page_size_preference or self.paginate_by
        self.hot_period = kwargs.get("day_amount") or self.hot_period

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        search_query = self.request.GET.get("query", "").lower()

        queryset = Question.objects.get_question_list(search_query)

        #* this just ORDER BY rating_total DESC
        queryset = Question.objects.get_hot_questions(queryset, self.hot_period, self.current_user)

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["main_title_extra"] = f"last {self.hot_period} {"day" if self.hot_period == 1 else "days"}"

        return context


# TODO Make this accessible from footer or smth
class TagsQuestionListingView(BaseContextViewMixin, ListView):
    template_name = "question-listing.html"
    page_title = "Tags Question Listing"

    paginate_by = DEFAULT_PAGINATION_SIZE
    context_object_name = "questions"

    tag_slugs = set()

    def get(self, request, *args, **kwargs):
        self.paginate_by = self.page_size or self.paginate_by
        self.tag_slugs = {tag.strip() for tag in kwargs.get("tags_list").split(TAG_DELIMITER) if tag.strip()}

        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        search_query = self.request.GET.get("query", "").lower()

        queryset = Question.objects.get_question_list(search_query)

        queryset = Question.objects.exclude_disliked_by_user(queryset, self.current_user)

        if self.tag_slugs:
            for tag_slug in self.tag_slugs:
                queryset = queryset.filter(tags__slug__iexact=tag_slug) #? Maybe use __icontains

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["main_title"] = "Tag: " if len(self.tag_slugs) == 1 else "Tags: "
        context["main_title_extra"] = ", ".join(self.tag_slugs)

        return context


class NewQuestionView(BaseContextViewMixin, TemplateView):
    template_name = "new-question.html"
    page_title = "New Question"
    main_title = "New Question"
