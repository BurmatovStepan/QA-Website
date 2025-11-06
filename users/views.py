from typing import Any
from django.http.response import HttpResponse as HttpResponse
from django.views.generic import TemplateView
from common.mixins import BaseContextViewMixin
from django.http import Http404



MOCK_USERS = []
MOCK_ACTIVITIES = []
for i in range(1, 101):
    MOCK_USERS.append({
        "id": i,
        "login": "idk",
        "password": "still no clue",
        "email": "whydidi@add.this",
        "displayed_name": "Remembered",
        "avatar": "assets/avatar.svg",
        "rating": i,
        "total_questions_asked": i,
        "total_answers_posted": i,
        "disliked_questions": [i + j for j in range(5)],
    })

    MOCK_ACTIVITIES.append({
        "id": i,
        "user_id": i,
        "type": i % 3 + 1,
        "target_id": i,
        "date": "5-11-2025",
    })



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

        user["recent_activities"] = get_recent_activities(user_id) # type: ignore

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

        display_text = ""
        target_url = "#"

        match activity_type:
            case 1:
                # question_title =
                # target_url =
                display_text = f"Created question ..."

            case 2:
                # answer_snippet =
                # target_url =
                display_text = f"Liked ..."

            case 3:
                # target_url =
                display_text = "Changed avatar"

        display_records.append({
            "link_url": target_url,
            "text": display_text
        })

    return display_records


class SettingsView(BaseContextViewMixin, TemplateView):
    template_name = "settings.html"
    page_title = "User Settings"
    main_title = "Settings: "

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        current_user_data = context.get("current_user_data")
        if (current_user_data is not None):
            context["user"] = current_user_data
            context["main_title_extra"] = current_user_data.get("displayed_name")
        else:
            raise Http404("Go log in")
        return context
