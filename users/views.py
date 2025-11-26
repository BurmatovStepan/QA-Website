from typing import Any

from django.contrib.auth import authenticate, login
from django.db.models.query import QuerySet
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, FormView, TemplateView

from common.constants import DEFAULT_PAGINATION_SIZE
from common.mixins import BaseContextViewMixin
from users.forms import LoginForm
from users.models import Activity, CustomUser


class LoginView(BaseContextViewMixin, FormView):
    template_name = "login.html"
    form_class = LoginForm

    page_title = "AskMe | Log in"
    main_title = "Log In"

    def form_valid(self, form):
        user_login = form.cleaned_data.get("login")
        user_password = form.cleaned_data.get("password")

        user = authenticate(self.request, username=user_login, password=user_password)
        if user:
            login(self.request, user)
            return redirect(reverse("profile", kwargs={"id": user.id}), code=303)

        form.add_error(None, "Неверный логин или пароль")
        return self.form_invalid(form)

class RegisterView(BaseContextViewMixin, TemplateView):
    template_name = "register.html"
    page_title = "AskMe | Registration"
    main_title = "Registration"


class ProfileView(BaseContextViewMixin, DetailView):
    template_name = "profile.html"
    model = CustomUser
    context_object_name = "viewed_user"

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get("id")

        if user_id is None and self.current_user is None:
            return render(request, "401.html", status=401)

        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[CustomUser]:
        return CustomUser.objects.get_user_detail()

    def get_object(self, queryset: QuerySet[CustomUser] | None = None):
        if queryset is None:
            queryset = self.get_queryset()

        user_id = self.kwargs.get("id")

        if user_id is None and self.current_user is not None:
            return self.current_user

        user = get_object_or_404(queryset, id=user_id)

        return user

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
            return render(request, "401.html", status=401)

        return super().get(request, *args, **kwargs)
