from django.contrib import admin
from django.urls import include, path

from qa.views import HomepageView

urlpatterns = [
    path("", HomepageView.as_view(), name="homepage"),

    path("questions/", include("qa.urls")),
    path("users/", include("users.urls")),
    
    path("test/", include("tests.urls")),
    path("admin/", admin.site.urls),
]
