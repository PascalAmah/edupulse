"""
Authentication URL configuration for EduPulse project.

This module contains URL patterns for authentication endpoints.
Dev 1 responsibility: Auth & User Management
"""

from django.urls import path
from ..views.auth_views import (
    RegisterView, LoginView, LogoutView, UserProfileView,
    PasswordResetRequestView, PasswordResetConfirmView,
    ChangePasswordView, RefreshTokenView, StudentProtectedDummyView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Password management endpoints
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/change/', ChangePasswordView.as_view(), name='change_password'),

    path('student-protected/', StudentProtectedDummyView.as_view(), name='student_protected'),
]