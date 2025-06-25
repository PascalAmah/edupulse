"""
Custom permission classes for EduPulse project.

This module contains reusable permission classes that can be used across
different views in the project.
"""

from rest_framework import permissions
from django.contrib.auth.models import User


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    
    def has_permission(self, request, view):
        # TODO: Implement admin user check
        # Check if user is authenticated and has admin privileges
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # TODO: Implement object-level permission check
        # Check if user is the owner of the object
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers to create/edit content.
    """
    
    def has_permission(self, request, view):
        # TODO: Implement teacher permission check
        # Check if user has teacher role
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to teachers
        return hasattr(request.user, 'profile') and request.user.profile.role == 'teacher'


class IsStudentOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow students to access student-specific content.
    """
    
    def has_permission(self, request, view):
        # TODO: Implement student permission check
        # Check if user has student role
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to students
        return hasattr(request.user, 'profile') and request.user.profile.role == 'student'


class HasQuizAccess(permissions.BasePermission):
    """
    Custom permission to check if user has access to a specific quiz.
    """
    
    def has_object_permission(self, request, view, obj):
        # TODO: Implement quiz access check
        # Check if user:
        # - Is enrolled in the course containing the quiz
        # - Has completed prerequisites
        # - Quiz is available (not expired, etc.)
        return True


class CanSubmitQuiz(permissions.BasePermission):
    """
    Custom permission to check if user can submit a quiz.
    """
    
    def has_permission(self, request, view):
        # TODO: Implement quiz submission permission check
        # Check if user:
        # - Has started the quiz
        # - Hasn't exceeded time limit
        # - Hasn't already submitted
        return True 