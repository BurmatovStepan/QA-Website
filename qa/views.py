from random import randint
from typing import Any

from django.http import Http404
from django.http.response import HttpResponse as HttpResponse
from django.views.generic import TemplateView

MOCK_QUESTIONS = []
for i in range(1, 101):
    MOCK_QUESTIONS.append({"id": i, "rating": randint(-100, 100), "title": f"[{i}] Where do I find clothes?", "content": "So I'm at a store and I can't find them, there's only soup. I went through every aisle but there was only more soup. What do I do? This question description is significantly longer than the over one so I have to add more styles to fix that. Quick brown fox jumped over the lazy dog. I don't have lorem ipsum copypasta. Remebered that br exists."})


class HomepageView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["mock_questions"] = MOCK_QUESTIONS

        return context


class QuestionDiscussionView(TemplateView):
    template_name = "question.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        question_id = kwargs.get("id")
        found_question = next(
            (question for question in MOCK_QUESTIONS if question["id"] == question_id),
            None
        )

        if (found_question is None):
            raise Http404(f"Question with ID '{question_id}' does not exist.")

        context["question"] = found_question

        return context


class QuestionListingView(TemplateView):
    template_name = "question-listing.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["mock_questions"] = MOCK_QUESTIONS

        return context


class NewQuestionView(TemplateView):
    template_name = "new-question.html"
