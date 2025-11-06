from django.urls import path

from qa.views import HomepageView, NewQuestionView, QuestionDiscussionView, QuestionListingView

urlpatterns = [
    path("", HomepageView.as_view(), name="homepage"),
    path("question/<int:id>/", QuestionDiscussionView.as_view(), name="question_discussion"),
    path("listing/", QuestionListingView.as_view(), name="question_listing"),
    path("new-question/", NewQuestionView.as_view(), name="new_question")
]
