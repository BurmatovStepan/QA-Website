from django.urls import path

from tests.views import Error404View

urlpatterns = [
    path("404/", Error404View.as_view(), name="error_404"),
]
