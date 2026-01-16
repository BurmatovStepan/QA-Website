from django.urls import path
from simple_wsgi.views import TestView

urlpatterns = [
    path("", TestView.as_view(), name="test_view"),
]
