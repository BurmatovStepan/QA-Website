from django.urls import path

from qa.ajax_views import CreateAnswerView, ToggleVoteView
from qa.views import (HotQuestionsView, NewQuestionView,
                      QuestionDiscussionView, TagsQuestionListingView)

urlpatterns = [
    path("new-question/", NewQuestionView.as_view(), name="new_question"),

    path("question/<int:id>/", QuestionDiscussionView.as_view(), name="question_discussion_no_slug"),
    path("question/<int:id>/<str:slug>/", QuestionDiscussionView.as_view(), name="question_discussion"),

    path("hot-questions/", HotQuestionsView.as_view(), name="hot_questions"),
    path("hot-questions/<int:day_amount>/", HotQuestionsView.as_view(), name="hot_questions_period"),

    path("tags/<str:tags_list>/", TagsQuestionListingView.as_view(), name="tag_question_listing"),

    path("question/<int:id>/answer/submit/", CreateAnswerView.as_view(), name="question_answer_submit"),
    path("<str:model_type>/<int:id>/vote/", ToggleVoteView.as_view(), name="toggle_vote"),
]
