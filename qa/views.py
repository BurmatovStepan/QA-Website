from typing import Any

from django.http import Http404
from django.http.response import HttpResponse as HttpResponse
from django.views.generic import TemplateView

from common.mixins import BaseContextViewMixin

MOCK_QUESTIONS = []
MOCK_ANSWERS = []
for i in range(1, 101):
    MOCK_QUESTIONS.append({
        "id": i,
        "author_id": i,
        "rating": i,
        "title": f"[{i}] Where do I find clothes?",
        "content": "So I'm at a store and I can't find them, there's only soup. I went through every aisle but there was only more soup. What do I do? This question description is significantly longer than the over one so I have to add more styles to fix that. Quick brown fox jumped over the lazy dog. I don't have lorem ipsum copypasta. Remebered that br exists.",
        "tags": ["soup", "tf2"],
        "answer_amount": i,
        "creation_date": "5-11-2025",
        "is_hot": i % 2,
    })

    MOCK_ANSWERS.append({
        "id": i,
        "question_id": i,
        "author_id": i,
        "rating": i,
        "content": "I've never had a similar experience so I consider myself an expert is this field, so I think you should buy some soup.",
        "is_correct": i % 2,
    })


class HomepageView(BaseContextViewMixin, TemplateView):
    template_name = "index.html"
    page_title = "AskMe"
    main_title = "New Questions"
    main_title_extra = "Hot Questions"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        current_user_data = context.get("current_user_data")
        if (current_user_data is not None):
            disliked_ids = current_user_data.get("disliked_questions", [])
            context["mock_questions"] = sorted(MOCK_QUESTIONS, key=lambda question: question["id"] in disliked_ids)

        else:
            context["mock_questions"] = MOCK_QUESTIONS

        return context


class QuestionDiscussionView(BaseContextViewMixin, TemplateView):
    template_name = "question.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        question_id = kwargs.get("id")
        found_question = next(
            (question for question in MOCK_QUESTIONS if question.get("id") == question_id),
            None
        )

        if (found_question is None):
            raise Http404(f"Question with ID '{question_id}' does not exist.")

        context["question"] = found_question
        context["page_title"] = f"Question | {found_question.get("title")}"

        found_answers = [
            answer for answer in MOCK_ANSWERS if answer.get("question_id") == question_id
        ]
        context["mock_answers"] = found_answers

        return context


class QuestionListingView(BaseContextViewMixin, TemplateView):
    template_name = "question-listing.html"
    page_title = "Question Listing"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["mock_questions"] = MOCK_QUESTIONS

        # TODO Actual titles
        context["main_title"] = "IDK"
        context["main_title_extra"] = "uh"

        return context


class NewQuestionView(BaseContextViewMixin, TemplateView):
    template_name = "new-question.html"
    page_title = "New Question"
    main_title = "New Question"
