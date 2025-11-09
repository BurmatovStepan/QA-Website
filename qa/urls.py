from django.urls import path

from qa.views import (HotQuestionsView, NewQuestionView,
                      QuestionDiscussionView, TagsQuestionListingView)

urlpatterns = [
    path("new-question/", NewQuestionView.as_view(), name="new_question"),
    path("question/<int:id>/", QuestionDiscussionView.as_view(), name="question_discussion"),

    path("hot-questions/", HotQuestionsView.as_view(), name="hot_questions"),
    path("hot-questions/<int:day_amount>/", HotQuestionsView.as_view(), name="hot_questions_period"),

    path("tags/<str:tags_list>/", TagsQuestionListingView.as_view(), name="tag_question_listing")
]
