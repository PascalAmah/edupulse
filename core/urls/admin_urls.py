"""
Admin URL patterns for EduPulse project.
"""

from django.urls import path
from ..views.admin_views import (
    AdminUserListView,
    AdminUserDetailView,
    AdminQuizListView,
    AdminQuizDetailView,
    AdminSystemAnalyticsView,
    AdminCategoryListView,
)

urlpatterns = [
    # User management
    path('users/', AdminUserListView.as_view(), name='admin-users-list'),
    path('users/<int:user_id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    
    # Quiz management
    path('quizzes/', AdminQuizListView.as_view(), name='admin-quizzes-list'),
    path('quizzes/<int:quiz_id>/', AdminQuizDetailView.as_view(), name='admin-quiz-detail'),
    
    # System analytics
    path('analytics/', AdminSystemAnalyticsView.as_view(), name='admin-analytics'),
    
    # Category management
    path('categories/', AdminCategoryListView.as_view(), name='admin-categories-list'),
] 