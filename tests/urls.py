from django.urls import path

from tests.views import test_404

urlpatterns = [
    path("404/", test_404, name="error_404"),
]
