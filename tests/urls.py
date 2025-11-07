from django.urls import path

from tests.views import Error404View, Error401View

urlpatterns = [
    path("404/", Error404View.as_view(), name="error_404"),
    path("401/", Error401View.as_view(), name="error_401"),
]
