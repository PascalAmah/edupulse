"""
Custom permission classes for EduPulse project.

This module contains reusable permission classes that can be used across
different views in the project.
"""

from rest_framework import permissions
from django.contrib.auth.models import User
from django.utils import timezone


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and 
            (user.is_staff or 
             (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'))
        )


class IsAdminOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins (no read access for others).
    """
    
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and
            (user.is_staff or 
             (hasattr(user, 'profile') and user.profile.role == 'admin'))
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        # Handle different object types that might have different owner fields
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        else:
            # If object doesn't have a clear owner field, deny access
            return False


class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers to create/edit content.
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        # Allow read-only methods for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return user.is_authenticated
        
        # Write permissions are only allowed to teachers and admins
        return (
            user.is_authenticated and
            hasattr(user, 'profile') and
            user.profile.role in ['teacher', 'admin']
        )


class IsTeacherOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers (no read access for others).
    """
    
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and
            hasattr(user, 'profile') and
            user.profile.role == 'teacher'
        )


class IsStudentOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow students to access student-specific content.
    """
    
    def has_permission(self, request, view):
        # Allow read-only methods for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to students
        user = request.user
        return (
            user.is_authenticated and
            hasattr(user, 'profile') and
            user.profile.role == 'student'
        )


class IsStudentOnly(permissions.BasePermission):
    """
    Custom permission to only allow students (no read access for others).
    """
    
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and
            hasattr(user, 'profile') and
            user.profile.role == 'student'
        )


class HasQuizAccess(permissions.BasePermission):
    """
    Custom permission to check if user has access to a specific quiz.
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Admins and teachers have access to all quizzes
        if hasattr(user, 'profile'):
            if user.profile.role in ['admin', 'teacher']:
                return True
        
        # For students, check quiz availability and enrollment
        if hasattr(obj, 'is_active') and not obj.is_active:
            return False
        
        # Check if quiz has expired
        if hasattr(obj, 'expires_at') and obj.expires_at:
            if timezone.now() > obj.expires_at:
                return False
        
        # Check if quiz has started (if it has a start date)
        if hasattr(obj, 'starts_at') and obj.starts_at:
            if timezone.now() < obj.starts_at:
                return False
        
        # If quiz has enrollment requirements, check them
        if hasattr(obj, 'course') and obj.course:
            # Check if user is enrolled in the course
            if hasattr(obj.course, 'enrolled_users'):
                if user not in obj.course.enrolled_users.all():
                    return False
        
        # If quiz has prerequisites, check them
        if hasattr(obj, 'prerequisites') and obj.prerequisites.exists():
            # This would need to be implemented based on your quiz model structure
            # For now, we'll assume prerequisites are met
            pass
        
        return True


class CanSubmitQuiz(permissions.BasePermission):
    """
    Custom permission to check if user can submit a quiz.
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Get quiz_id from URL parameters or request data
        quiz_id = view.kwargs.get('quiz_id') or request.data.get('quiz_id')
        
        if not quiz_id:
            return False
        
        # Import here to avoid circular imports
        from quizzes.models import Quiz, QuizAttempt
        
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return False
        
        # Check if user has access to the quiz
        from common.permissions import HasQuizAccess
        quiz_access = HasQuizAccess()
        if not quiz_access.has_object_permission(request, view, quiz):
            return False
        
        # Check if user has already submitted this quiz
        existing_attempt = QuizAttempt.objects.filter(
            user=user,
            quiz=quiz,
            completed_at__isnull=False
        ).first()
        
        if existing_attempt:
            return False
        
        # Check if user has an active attempt that hasn't expired
        active_attempt = QuizAttempt.objects.filter(
            user=user,
            quiz=quiz,
            completed_at__isnull=True
        ).first()
        
        if active_attempt:
            # Check if the attempt has exceeded time limit
            if hasattr(quiz, 'time_limit') and quiz.time_limit:
                time_elapsed = timezone.now() - active_attempt.started_at
                if time_elapsed.total_seconds() > quiz.time_limit * 60:  # Convert minutes to seconds
                    return False
        
        return True 