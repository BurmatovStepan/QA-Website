from typing import Any

from django.core.cache import cache

from common.utils import (safe_int_conversion, update_best_members,
                    update_popular_tags)


class BaseContextViewMixin:
    page_title = None
    main_title = None
    main_title_extra = None

    current_user = None

    items_per_page = None

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated:
            self.current_user = user
        else:
            self.current_user = None

        page_size = self.request.GET.get("page-size")
        self.items_per_page = safe_int_conversion(page_size)

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
            best_members = update_best_members()

        if popular_tags is None:
            popular_tags = update_popular_tags()

        context["best_members"] = best_members
        context["popular_tags"] = popular_tags

        return context
