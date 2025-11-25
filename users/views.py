from typing import Any
from common.constants import DEFAULT_PAGINATION_SIZE
from django.db.models.query import QuerySet
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, TemplateView

from common.mixins import BaseContextViewMixin
from users.models import Activity, CustomUser

class LoginView(BaseContextViewMixin, TemplateView):
    template_name = "login.html"
    page_title = "AskMe | Log in"
    main_title = "Log In"


class RegisterView(BaseContextViewMixin, TemplateView):
    template_name = "register.html"
    page_title = "AskMe | Registration"
    main_title = "Registration"


class ProfileView(BaseContextViewMixin, DetailView):
    template_name = "profile.html"
    model = CustomUser
    context_object_name = "viewed_user"

    def get_queryset(self) -> QuerySet[CustomUser]:
        return CustomUser.objects.get_user_detail()

    def get_object(self, queryset: QuerySet[CustomUser] | None = None):
        if queryset is None:
            queryset = self.get_queryset()

        user_id = self.kwargs.get("id")
        question = get_object_or_404(queryset, id=user_id)

        return question

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.object

        page_size = self.page_size or DEFAULT_PAGINATION_SIZE
        activities_queryset = Activity.objects.get_recent_activities(user)
        display_records = [activity.get_display_info(page_size) for activity in activities_queryset]

        # TODO Add some styling to recent activities
        context["recent_activities"] = display_records

        display_name = user.display_name if user.display_name else user.login
        context["page_title"] = f"User | {display_name}"

        return context


class SettingsView(BaseContextViewMixin, TemplateView):
    template_name = "settings.html"
    page_title = "User Settings"
    main_title = "Settings: "

    def get(self, request, *args, **kwargs):
        if self.current_user is None:
            return redirect("error_401")

        return super().get(request, *args, **kwargs)
