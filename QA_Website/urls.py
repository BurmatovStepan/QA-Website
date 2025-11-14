from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from qa.views import HomepageView

urlpatterns = [
    path("", HomepageView.as_view(), name="homepage"),

    path("questions/", include("qa.urls")),
    path("users/", include("users.urls")),

    path("test/", include("tests.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
