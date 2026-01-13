from django.template.defaultfilters import date
from django.forms.models import model_to_dict
from django.db import transaction
from django.db.models import F
from django.forms import ValidationError
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import View

from qa.forms import AnswerForm
from qa.models import Answer, AnswerVote, Question, QuestionVote
from qa.constants import LIKE, DISLIKE
from users.models import Activity
from common.mixins import APIAuthRequiredMixin

# TODO Make enum for error types
class CreateAnswerView(APIAuthRequiredMixin, View):
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

                return JsonResponse({
                    "success": True,
                    "answer_data": {
                        "id": new_answer.id,
                        "created_at": date(new_answer.created_at, "DATETIME_FORMAT"),
                        "content": new_answer.content,
                    }
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


class ToggleQuestionVoteView(APIAuthRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        question_id = kwargs.get("id")
        vote_type_raw = kwargs.get("vote_type")

        question = Question.objects.filter(id=question_id).first()

        if question is None:
            return JsonResponse({
                "success": False,
                "error_type": f"question_not_found",
                "message": f"Question with ID {question_id} does not exist."
            }, status=404)

        try:
            vote_type = int(vote_type_raw)
        except (TypeError, ValueError):
            return JsonResponse({
                "success": False,
                "message": "Некорректный формат типа оценки"
            }, status=400)

        if vote_type not in [LIKE, DISLIKE]:
            return JsonResponse({
                "success": False,
                "message": "Неизвестный тип оценки.",
            }, status=400)

        return question.add_vote(request.user, vote_type)


class ToggleAnswerVoteView(APIAuthRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        answer_id = kwargs.get("id")
        vote_type_raw = kwargs.get("vote_type")

        answer = Answer.objects.filter(id=answer_id).first()

        if answer is None:
            return JsonResponse({
                "success": False,
                "error_type": f"question_not_found",
                "message": f"Question with ID {answer_id} does not exist."
            }, status=404)

        try:
            vote_type = int(vote_type_raw)
        except (TypeError, ValueError):
            return JsonResponse({
                "success": False,
                "message": "Некорректный формат типа оценки"
            }, status=400)

        if vote_type not in [LIKE, DISLIKE]:
            return JsonResponse({
                "success": False,
                "message": "Неизвестный тип оценки.",
            }, status=400)

        return answer.add_vote(request.user, vote_type)


# TODO Allow unmark answer correct
class MarkAnswerCorrectView(APIAuthRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        question_id = kwargs.get("question_id")
        answer_id = kwargs.get("answer_id")

        question = Question.objects.filter(id=question_id).prefetch_related().first()

        if question is None:
            return JsonResponse({
                "success": False,
                "error_type": f"question_not_found",
                "message": f"Question with ID {question_id} does not exist."
            }, status=404)

        if question.author != request.user:
            return JsonResponse({
                "success": False,
                "error_type": f"not_an_author",
                "message": f"You can not mark answers correct under other people's question."
            }, status=403)

        answer = question.answers.filter(id=answer_id).first()
        if answer is None:
            return JsonResponse({
                "success": False,
                "error_type": f"answer_not_found",
                "message": f"Answer with ID {answer_id} does not exist."
            }, status=404)

        try:
            with transaction.atomic():
                new_activity = Activity(
                    user=answer.author,
                    type="A_MARKED_CORRECT",
                    target=answer
                )
                new_activity.save()

                answer.is_correct = True
                answer.save()

                return JsonResponse({
                    "success": True
                }, status=200)

        except Exception as e:
            print(e)

        return JsonResponse({
            "success": False,
            "message": "Произошла непредвиденная ошибка. Попробуйте еще раз.",
        }, status=500)
