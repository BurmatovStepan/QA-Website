from typing import Any

from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, FormView

from common.constants import DEFAULT_PAGINATION_SIZE
from common.mixins import (AnonymousRequiredMixin, BaseContextViewMixin,
                           LoginRequiredMixin)
from users.forms import LoginForm, RegisterForm, SettingsFrom
from users.models import Activity, CustomUser
from users.utilities import get_safe_redirect_url


# TODO make settings updated popup
class LoginView(AnonymousRequiredMixin, BaseContextViewMixin, FormView):
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

            redirect_to = get_safe_redirect_url(self.request, self.request.GET.get("next"), "current_user_profile")
            return HttpResponseRedirect(redirect_to, status=303)

        form.add_error(None, "Неверный логин или пароль")
        return self.form_invalid(form)


class RegisterView(AnonymousRequiredMixin, BaseContextViewMixin, FormView):
    template_name = "register.html"
    form_class = RegisterForm

    page_title = "AskMe | Registration"
    main_title = "Registration"

    def form_valid(self, form):
        try:
            with transaction.atomic():
                user_login = form.cleaned_data.get("login")
                user_email = form.cleaned_data.get("email")
                user_password = form.cleaned_data.get("password")
                user_display_name = form.cleaned_data.get("display_name")
                user_avatar = form.cleaned_data.get("avatar")

                new_user = CustomUser.objects.create_user(
                    login=user_login,
                    email=user_email,
                    password=user_password,
                    display_name=user_display_name,
                )

                if user_avatar:
                    new_user.avatar = user_avatar
                    new_user.save()

                login(self.request, new_user)

        except Exception as e:
            form.add_error(None, "Произошла ошибка при создании записи пользователя. Повторите попытку ещё раз.")
            return self.form_invalid(form)

        redirect_to = get_safe_redirect_url(self.request, self.request.GET.get("next"), "current_user_profile")
        return HttpResponseRedirect(redirect_to, status=303)


class ProfileView(BaseContextViewMixin, DetailView):
    template_name = "profile.html"
    model = CustomUser
    context_object_name = "viewed_user"

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get("id")

        if user_id is None and self.current_user is None:
            login_url = f"{reverse("login")}?next={request.path}"
            return HttpResponseRedirect(login_url)

        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[CustomUser]:
        return CustomUser.objects.get_user_detail()

    def get_object(self, queryset: QuerySet[CustomUser] | None = None):
        if queryset is None:
            queryset = self.get_queryset()

        user_id = self.kwargs.get("id")

        if user_id is None and self.current_user is not None:
            user_id = self.current_user.id

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

# TODO Make successful settings update popup
class SettingsView(LoginRequiredMixin, BaseContextViewMixin, FormView):
    template_name = "settings.html"
    form_class = SettingsFrom

    page_title = "User Settings"
    main_title = "Settings: "

    def get_initial(self):
        return  {
            "login": self.current_user.login,
            "email": self.current_user.email,
            "display_name": self.current_user.display_name,
            "avatar": self.current_user.avatar,
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.current_user
        return kwargs

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.current_user.login = form.cleaned_data.get("login")
                self.current_user.email = form.cleaned_data.get("email")
                self.current_user.display_name = form.cleaned_data.get("display_name")

                new_avatar = form.cleaned_data.get("avatar")
                clear_avatar = form.cleaned_data.get('clear_avatar')

                if clear_avatar:
                    self.current_user.avatar.delete(save=False)
                    self.current_user.avatar = None
                elif new_avatar:
                    self.current_user.avatar = new_avatar

                self.current_user.save()
                return HttpResponseRedirect(reverse("settings"), status=303)

        except Exception as e:
            form.add_error(None, "Произошла ошибка при изменении записи пользователя. Повторите попытку ещё раз.")
            return self.form_invalid(form)


@require_POST
def logout_view(request):
    logout(request)

    redirect_to = get_safe_redirect_url(request, request.POST.get("next"))

    return HttpResponseRedirect(redirect_to, status=303)
