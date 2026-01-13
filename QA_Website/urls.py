import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from qa.ajax_views import ToggleQuestionVoteView, ToggleAnswerVoteView
from qa.views import HomepageView

urlpatterns = [
    path("", HomepageView.as_view(), name="homepage"),

    path("questions/", include("qa.urls")),
    path("users/", include("users.urls")),

    path("vote/question/<int:id>/<str:vote_type>/", ToggleQuestionVoteView.as_view(), name="toggle_question_vote"),
    path("vote/answer/<int:id>/<str:vote_type>/", ToggleAnswerVoteView.as_view(), name="toggle_answer_vote"),

    path("test/", include("simple_wsgi.urls")),

    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
