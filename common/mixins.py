from typing import Any

from django.core.cache import cache
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse

from common.constants import CACHE_TTL, DEFAULT_PAGINATION_SIZE
from users.models import CustomUser


class BaseContextViewMixin:
    page_title: str | None = None
    main_title: str | None = None
    main_title_extra: str | None = None

    current_user: CustomUser | None = None

    page_size: int | None = None

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if user.is_authenticated:
            self.current_user = user
            self.page_size = self.current_user.page_size_preference or DEFAULT_PAGINATION_SIZE

        else:
            self.current_user = None
            self.page_size = DEFAULT_PAGINATION_SIZE

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        from qa.models import Tag

        context = super().get_context_data(**kwargs)

        context["page_title"] = self.page_title or "Default Page Name"
        context["main_title"] = self.main_title
        context["main_title_extra"] = self.main_title_extra

        context["current_user"] = self.current_user

        best_members = cache.get("best_members")
        popular_tags = cache.get("popular_tags")

        if best_members is None:
            best_members = CustomUser.objects.get_best_members()
            cache.set("best_members", best_members, timeout=CACHE_TTL)

        if popular_tags is None:
            popular_tags = Tag.objects.get_popular_tags()
            cache.set("popular_tags", popular_tags, timeout=CACHE_TTL)

        context["best_members"] = best_members
        context["popular_tags"] = popular_tags

        return context


class LoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        login_url = f"{reverse("login")}?next={request.path}"

        return HttpResponseRedirect(login_url, status=303)


class AnonymousRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("current_user_profile"), status=303)

        return super().dispatch(request, *args, **kwargs)


class APIAuthRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not (request.user and request.user.is_authenticated):
            return JsonResponse({
                "success": False,
                "error_type": "authentication_required",
                "message": "You must be logged in to perform this action."
            }, status=401)
        return super().dispatch(request, *args, **kwargs)


class VotableMixin:
    def add_vote(self, user: CustomUser, vote_type: int):
        with transaction.atomic():
            try:
                existing_vote = self.votes.filter(user=user).first()
                rating_delta = 0

                vote_status = "none"

                if existing_vote:
                    if existing_vote.type == vote_type:
                        rating_delta = -vote_type
                        existing_vote.delete()

                    else:
                        rating_delta = 2 * vote_type
                        existing_vote.type = vote_type
                        existing_vote.save()

                        vote_status = "liked" if existing_vote.type == 1 else "disliked"

                else:
                    rating_delta = vote_type
                    new_vote = self.votes.create(
                        user=user,
                        type=vote_type,
                    )

                    vote_status = "liked" if new_vote.type == 1 else "disliked"

                if rating_delta != 0:
                    self.rating_total = F("rating_total") + rating_delta
                    self.save(update_fields=["rating_total"])

                    self.refresh_from_db()

                return JsonResponse({
                    "success": True,
                    "new_rating": self.rating_total,
                    "vote_status": vote_status,
                }, status=200)

            except Exception as e:
                print(e)

        return JsonResponse({
            "success": False,
            "message": "Произошла непредвиденная ошибка. Попробуйте еще раз.",
        }, status=500)
