from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("qa.urls")),
    path("", include("users.urls")),
    path("test/", include("tests.urls")),
    path("admin/", admin.site.urls),
]
