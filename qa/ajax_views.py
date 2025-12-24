from django.forms import ValidationError
from django.db import transaction
from django.db.models import F

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import View

from qa.models import LIKE, DISLIKE
from common.mixins import LoginRequiredMixin, BaseContextViewMixin
from qa.forms import AnswerForm
from qa.models import Question, QuestionVote, Answer, AnswerVote


# TODO Make enum for error types
class CreateAnswerView(LoginRequiredMixin, BaseContextViewMixin, View):
    def post(self, request, *args, **kwargs):
        question_id = kwargs.get("id")
        question = Question.objects.filter(id=question_id).prefetch_related().first()

        if question is None:
            return JsonResponse({
                "success": False,
                "error_type": "question_not_found",
                "message": f"Question with ID {question_id} does not exist."
            }, status=404)

        form = AnswerForm(
            request.POST,
            author=request.user,
            question=question
        )

        if form.is_valid():
            try:
                new_answer = form.save()

                answer_card_html = render_to_string(
                    "snippets/answer-card.html",
                    {"answer": new_answer, "question": question,"request": request, "current_user": self.current_user}
                )

                return JsonResponse({
                    "success": True,
                    "answer_id": new_answer.id,
                    "answer_html": answer_card_html,
                }, status=201)

            except ValidationError as e:
                form.add_error(None, e)

            except Exception as e:
                print(e)
                form.add_error(None, "Произошла непредвиденная ошибка. Попробуйте еще раз.")

        return JsonResponse({
            "success": False,
            "errors": form.errors,
            "error_type": "validation_error",
        }, status=400)


class ToggleVoteView(LoginRequiredMixin, BaseContextViewMixin, View):
    _MAPPING = {
        "question": (Question, QuestionVote, "question"),
        "answer": (Answer, AnswerVote, "answer"),
    }

    def post(self, request, *args, **kwargs):
        model_type = kwargs.get("model_type")
        object_id = kwargs.get("id")

        try:
            vote_type = int(request.POST.get("vote_type"))
        except (TypeError, ValueError):
            return JsonResponse({
                "success": False,
                "errors": "Некорректный формат типа оценки"
            }, status=400)

        if vote_type not in [LIKE, DISLIKE]:
            return JsonResponse({
                "success": False,
                "errors": "Неизвестный тип оценки.",
            }, status=400)

        mapping_data = self._MAPPING.get(model_type)

        if mapping_data is None:
            return JsonResponse({
                "success": False,
                "errors": "Неизвестная модель.",
            }, status=400)

        Model, VoteModel, relation_field = mapping_data

        obj = Model.objects.filter(id=object_id).first()

        if obj is None:
            return JsonResponse({
                "success": False,
                "error_type": f"{relation_field}_not_found",
                "message": f"{relation_field.capitalize()} with ID {object_id} does not exist."
            }, status=404)

        with transaction.atomic():
            try:
                existing_vote = VoteModel.objects.filter(user=self.current_user, **{relation_field: obj}).first()
                rating_delta = 0

                if existing_vote:
                    if existing_vote.type == vote_type:
                        rating_delta = -vote_type
                        existing_vote.delete()

                    else:
                        rating_delta = 2 * vote_type
                        existing_vote.type = vote_type
                        existing_vote.save()
                else:
                    rating_delta = vote_type
                    VoteModel.objects.create(
                        user=self.current_user,
                        type=vote_type,
                        **{relation_field: obj},
                    )

                if rating_delta != 0:
                    obj.rating_total = F("rating_total") + rating_delta
                    obj.save(update_fields=["rating_total"])

                    obj.refresh_from_db()

                return JsonResponse({
                    "success": True,
                    "new_rating": obj.rating_total,
                }, status=200)

            except Exception as e:
                print(e)

        return JsonResponse({
            "success": False,
            "errors": "Произошла непредвиденная ошибка. Попробуйте еще раз.",
        }, status=500)
