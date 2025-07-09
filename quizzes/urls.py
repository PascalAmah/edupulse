# quizzes/urls.py

from django.urls import path

# Fetch quiz endpoints
from .views.fetch_quiz import (
    QuizListView,
    QuizDetailView,
    QuizQuestionsView,
    QuizQuestionDetailView,
    QuizProgressView,
    UserQuizAttemptsView,
)

# Quiz submission endpoints
from .views.submit_quiz import (
    SubmitQuizView,
    QuizResultView,
    SaveAnswerView,
    QuizFeedbackView,
    RetakeQuizView,
    QuizAnalyticsView,
)

urlpatterns = [
    # Fetch quiz endpoints
    path('', QuizListView.as_view(), name='quiz-list'),
    path('<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('<int:quiz_id>/questions/', QuizQuestionsView.as_view(), name='quiz-questions'),
    path('<int:quiz_id>/questions/<int:question_id>/', QuizQuestionDetailView.as_view(), name='quiz-question-detail'),
    path('<int:quiz_id>/progress/', QuizProgressView.as_view(), name='quiz-progress'),
    path('attempts/', UserQuizAttemptsView.as_view(), name='user-quiz-attempts'),

    # Quiz submission endpoints
    path('<int:quiz_id>/submit/', SubmitQuizView.as_view(), name='quiz-submit'),
    path('<int:quiz_id>/result/', QuizResultView.as_view(), name='quiz-result'),
    path('<int:quiz_id>/questions/<int:question_id>/answer/', SaveAnswerView.as_view(), name='save-answer'),
    path('<int:quiz_id>/feedback/', QuizFeedbackView.as_view(), name='quiz-feedback'),
    path('<int:quiz_id>/retake/', RetakeQuizView.as_view(), name='retake-quiz'),
    path('<int:quiz_id>/analytics/', QuizAnalyticsView.as_view(), name='quiz-analytics'),
]
