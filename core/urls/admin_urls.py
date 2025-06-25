"""
Admin URL configuration for EduPulse project.

This module contains URL patterns for admin user management endpoints.
Dev 1 responsibility: Auth & User Management
"""

from django.urls import path
from ..views.admin_views import (
    UserListView, UserDetailView, UserStatsView, BulkUserActionView,
    UserSessionListView, TerminateSessionView
)

urlpatterns = [
    # User management endpoints
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('users/stats/', UserStatsView.as_view(), name='user_stats'),
    path('users/bulk-action/', BulkUserActionView.as_view(), name='bulk_user_action'),
    
    # Session management endpoints
    path('sessions/', UserSessionListView.as_view(), name='user_session_list'),
    path('sessions/<int:session_id>/terminate/', TerminateSessionView.as_view(), name='terminate_session'),
] 