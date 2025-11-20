from django.urls import path

from users.views import LoginView, ProfileView, RegisterView, SettingsView

urlpatterns = [
    path("login/", LoginView.as_view(),  name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("<int:id>/", ProfileView.as_view(), name="profile"),
    path("me/settings/", SettingsView.as_view(), name="settings")
]
