from django.urls import path
from users.views import LoginView, RegisterView, ProfileView, SettingsView

urlpatterns = [
    path("login/", LoginView.as_view(),  name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("user/<int:id>/", ProfileView.as_view(), name="user"),
    path("settings/", SettingsView.as_view(), name="settings")
]
