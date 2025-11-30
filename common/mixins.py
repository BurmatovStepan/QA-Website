from typing import Any

from django.urls import reverse
from django.core.cache import cache

from django.shortcuts import render
from common.constants import DEFAULT_PAGINATION_SIZE
from qa.models import Tag
from django.http import HttpResponseRedirect
from users.models import CustomUser
from django.shortcuts import redirect

CACHE_TTL = 60 * 60 * 24

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
