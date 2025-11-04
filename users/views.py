from django.http.response import HttpResponse as HttpResponse
from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = "login.html"


class RegisterView(TemplateView):
    template_name = "register.html"


class ProfileView(TemplateView):
    template_name = "profile.html"


class SettingsView(TemplateView):
    template_name = "settings.html"
