from django.urls import path

from users.views import LoginView, ProfileView, RegisterView, SettingsView, logout_view

urlpatterns = [
    path("login/", LoginView.as_view(),  name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("<int:id>/", ProfileView.as_view(), name="profile"),
    path("me/", ProfileView.as_view(), name="current_user_profile"),
    path("me/settings/", SettingsView.as_view(), name="settings"),
    path("logout/", logout_view, name="logout")
]
