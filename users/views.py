from typing import Any
from django.http.response import HttpResponse as HttpResponse
from django.views.generic import TemplateView
from common.mixins import BaseContextViewMixin, MOCK_QUESTIONS, MOCK_ANSWERS, MOCK_USERS, MOCK_ACTIVITIES
from django.http import Http404


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
        user = next(
            (user for user in MOCK_USERS if user.get("id") == user_id),
            None
        )
        if (user is None):
            raise Http404(f"User with ID '{user_id}' does not exist.")

        user["recent_activities"] = get_recent_activities(user_id)[:10] # type: ignore

        context["user"] = user
        context["page_title"] = f"User | {user.get("displayed_name")}"

        return context

def get_recent_activities(user_id: int) -> list[dict[str, str]]:
    display_records = []
    user_activity_records = [
        record for record in MOCK_ACTIVITIES
        if record.get("user_id") == user_id
    ]

    for record in user_activity_records:
        activity_type = record.get("type")
        target_id = record.get("target_id")

        description = ""
        target_url = "#"

        match activity_type:
            case 1:
                # question_title =
                # target_url =
                description = f"Created question ..."

            case 2:
                # answer_snippet =
                # target_url =
                description = f"Liked ..."

            case 3:
                # target_url =
                description = "Changed avatar"

        display_records.append({
            "link_url": target_url,
            "description": description
        })

    return display_records


class SettingsView(BaseContextViewMixin, TemplateView):
    template_name = "settings.html"
    page_title = "User Settings"
    main_title = "Settings: "

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        current_user = context.get("current_user")
        if (current_user is None):
            raise Http404("Go log in")
        return context
