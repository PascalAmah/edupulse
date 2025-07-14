"""
Quiz URL configuration for EduPulse project.

This module contains URL patterns for quiz functionality.
Dev 2 responsibility: Quiz Logic
"""

from django.urls import path
from .views.fetch_quiz import (
    QuizListView,
    QuizDetailView,
    StartQuizView,
    QuizQuestionsView,
    QuizQuestionDetailView,
    QuizProgressView,
    UserQuizAttemptsView,
)
from .views.submit_quiz import (
    SubmitQuizView, QuizResultView, SaveAnswerView, QuizFeedbackView,
    RetakeQuizView, QuizAnalyticsView
)

urlpatterns = [
    # Fetch quiz endpoints
    path('', QuizListView.as_view(), name='quiz-list'),
    path('<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('<int:quiz_id>/start/', StartQuizView.as_view(), name='start-quiz'),
    path('<int:quiz_id>/questions/', QuizQuestionsView.as_view(), name='quiz-questions'),
    path('<int:quiz_id>/questions/<int:question_id>/', QuizQuestionDetailView.as_view(), name='quiz-question-detail'),
    path('<int:quiz_id>/progress/', QuizProgressView.as_view(), name='quiz-progress'),
    path('attempts/', UserQuizAttemptsView.as_view(), name='user-quiz-attempts'),
  
    # Quiz submission endpoints
    path('submit/', SubmitQuizView.as_view(), name='submit_quiz'),
    path('<int:quiz_id>/result/', QuizResultView.as_view(), name='quiz_result'),
    path('<int:quiz_id>/save-answer/', SaveAnswerView.as_view(), name='save_answer'),
    path('<int:quiz_id>/feedback/', QuizFeedbackView.as_view(), name='quiz_feedback'),
    path('<int:quiz_id>/retake/', RetakeQuizView.as_view(), name='retake_quiz'),
    path('<int:quiz_id>/analytics/', QuizAnalyticsView.as_view(), name='quiz_analytics'),
] 