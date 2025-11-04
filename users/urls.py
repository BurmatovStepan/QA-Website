from django.urls import path
from users.views import LoginView, RegisterView, ProfileView, SettingsView

urlpatterns = [
    path("login/", LoginView.as_view(),  name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("users/<int:id>/", ProfileView.as_view(), name="users"),
    path("settings/", SettingsView.as_view(), name="settings")
]
