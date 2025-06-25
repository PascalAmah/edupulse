"""
Quiz URL configuration for EduPulse project.

This module contains URL patterns for quiz functionality.
Dev 2 responsibility: Quiz Logic
"""

from django.urls import path
from .views.fetch_quiz import (
    QuizListView, QuizDetailView, StartQuizView, QuizQuestionView,
    QuizProgressView, QuizAttemptListView
)
from .views.submit_quiz import (
    SubmitQuizView, QuizResultView, SaveAnswerView, QuizFeedbackView,
    RetakeQuizView, QuizAnalyticsView
)

urlpatterns = [
    # Quiz fetching endpoints
    path('', QuizListView.as_view(), name='quiz_list'),
    path('<int:quiz_id>/', QuizDetailView.as_view(), name='quiz_detail'),
    path('start/', StartQuizView.as_view(), name='start_quiz'),
    path('<int:quiz_id>/question/<int:question_number>/', QuizQuestionView.as_view(), name='quiz_question'),
    path('<int:quiz_id>/progress/', QuizProgressView.as_view(), name='quiz_progress'),
    path('attempts/', QuizAttemptListView.as_view(), name='quiz_attempt_list'),
    
    # Quiz submission endpoints
    path('submit/', SubmitQuizView.as_view(), name='submit_quiz'),
    path('<int:quiz_id>/result/', QuizResultView.as_view(), name='quiz_result'),
    path('<int:quiz_id>/save-answer/', SaveAnswerView.as_view(), name='save_answer'),
    path('<int:quiz_id>/feedback/', QuizFeedbackView.as_view(), name='quiz_feedback'),
    path('<int:quiz_id>/retake/', RetakeQuizView.as_view(), name='retake_quiz'),
    path('<int:quiz_id>/analytics/', QuizAnalyticsView.as_view(), name='quiz_analytics'),
] 