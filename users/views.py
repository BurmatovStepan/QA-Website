from typing import Any

from django.http import Http404, HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from common.mixins import MOCK_USERS, BaseContextViewMixin
from common.utils import get_recent_activities

MAX_RECENT_ACTIVITIES = 10
class LoginView(BaseContextViewMixin, TemplateView):
    template_name = "login.html"
    page_title = "AskMe | Log in"
    main_title = "Log In"


class RegisterView(BaseContextViewMixin, TemplateView):
    template_name = "register.html"
    page_title = "AskMe | Registration"
    main_title = "Registration"


class ProfileView(BaseContextViewMixin, TemplateView):
    template_name = "profile.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        user_id = kwargs.get("id")
        user = MOCK_USERS.get(user_id)

        if user is None:
            raise Http404(f"User with ID '{user_id}' does not exist.")

        user["recent_activities"] = get_recent_activities(user_id)[:MAX_RECENT_ACTIVITIES]

        context["user"] = user
        context["page_title"] = f"User | {user["display_name"]}"

        return context


class SettingsView(BaseContextViewMixin, TemplateView):
    template_name = "settings.html"
    page_title = "User Settings"
    main_title = "Settings: "

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.current_user is None:
            return redirect("error_401")

        return super().get(request, *args, **kwargs)
