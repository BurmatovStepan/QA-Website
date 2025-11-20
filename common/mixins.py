from typing import Any

from django.core.cache import cache

from common.constants import DEFAULT_PAGINATION_SIZE
from qa.models import Tag
from users.models import CustomUser

CACHE_TTL = 60 * 60 * 24

class BaseContextViewMixin:
    page_title = None
    main_title = None
    main_title_extra = None

    current_user = None

    page_size = None

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated:
            self.current_user = user
            self.page_size = self.current_user.profile.page_size_preference or DEFAULT_PAGINATION_SIZE
        else:
            self.current_user = None
            self.page_size = DEFAULT_PAGINATION_SIZE

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
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


def safe_int_conversion(value: str):
    try: return int(value)
    except (ValueError, TypeError): return None
