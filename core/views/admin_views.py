"""
Admin views for EduPulse project.

This module contains admin-specific views for managing users, quizzes, and system analytics.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import UserProfile
from ..serializers import UserProfileSerializer
from quizzes.models import Quiz, QuizAttempt, Category
from common.permissions import IsAdminUser
from common.utils import calculate_quiz_statistics


class AdminUserListView(APIView):
    """
    GET /api/v1/admin/users/ endpoint to list all users with their roles.
    """
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get list of all users with their roles and profiles",
        manual_parameters=[
            openapi.Parameter(
                'role', openapi.IN_QUERY, description="Filter by user role", 
                type=openapi.TYPE_STRING, required=False,
                enum=['student', 'teacher', 'admin']
            ),
            openapi.Parameter(
                'search', openapi.IN_QUERY, description="Search by username or email", 
                type=openapi.TYPE_STRING, required=False
            ),
            openapi.Parameter(
                'page', openapi.IN_QUERY, description="Page number", 
                type=openapi.TYPE_INTEGER, required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="Users retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                                    'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'role': openapi.Schema(type=openapi.TYPE_STRING),
                                    'date_joined': openapi.Schema(type=openapi.TYPE_STRING),
                                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                }
                            )
                        )
                    }
                )
            ),
            403: openapi.Response(description="Access denied - Admin only"),
        }
    )
    def get(self, request):
        """
        Get all users with filtering and pagination.
        """
        # Get query parameters
        role = request.query_params.get('role')
        search = request.query_params.get('search')
        page = int(request.query_params.get('page', 1))
        page_size = 20
        
        # Start with all users
        users = User.objects.select_related('userprofile').all()
        
        # Apply filters
        if role:
            users = users.filter(userprofile__role=role)
        
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Calculate pagination
        total_count = users.count()
        start = (page - 1) * page_size
        end = start + page_size
        users = users[start:end]
        
        # Prepare response data
        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.userprofile.role if hasattr(user, 'userprofile') else 'student',
                'date_joined': user.date_joined.isoformat(),
                'is_active': user.is_active,
            })
        
        return Response({
            'count': total_count,
            'next': f"?page={page + 1}" if end < total_count else None,
            'previous': f"?page={page - 1}" if page > 1 else None,
            'results': user_data
        }, status=status.HTTP_200_OK)


class AdminUserDetailView(APIView):
    """
    GET /api/v1/admin/users/{user_id}/ endpoint to get detailed user information.
    """
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get detailed information about a specific user",
        manual_parameters=[
            openapi.Parameter(
                'user_id', openapi.IN_PATH, description="User ID", 
                type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="User details retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'role': openapi.Schema(type=openapi.TYPE_STRING),
                        'date_joined': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'quiz_attempts_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'average_score': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'quizzes_completed': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            404: openapi.Response(description="User not found"),
            403: openapi.Response(description="Access denied - Admin only"),
        }
    )
    def get(self, request, user_id):
        """
        Get detailed user information including quiz statistics.
        """
        user = get_object_or_404(User, id=user_id)
        
        # Get user's quiz statistics
        attempts = QuizAttempt.objects.filter(user=user)
        quiz_stats = attempts.aggregate(
            attempts_count=Count('id'),
            average_score=Avg('score'),
            completed_count=Count('id', filter=Q(completed_at__isnull=False))
        )
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.userprofile.role if hasattr(user, 'userprofile') else 'student',
            'date_joined': user.date_joined.isoformat(),
            'is_active': user.is_active,
            'quiz_attempts_count': quiz_stats['attempts_count'] or 0,
            'average_score': float(quiz_stats['average_score']) if quiz_stats['average_score'] else 0,
            'quizzes_completed': quiz_stats['completed_count'] or 0,
        }
        
        return Response(user_data, status=status.HTTP_200_OK)


class AdminQuizListView(APIView):
    """
    GET /api/v1/admin/quizzes/ endpoint to list all quizzes with admin statistics.
    """
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get list of all quizzes with admin statistics",
        manual_parameters=[
            openapi.Parameter(
                'category', openapi.IN_QUERY, description="Filter by category", 
                type=openapi.TYPE_STRING, required=False
            ),
            openapi.Parameter(
                'difficulty', openapi.IN_QUERY, description="Filter by difficulty", 
                type=openapi.TYPE_STRING, required=False,
                enum=['easy', 'medium', 'hard']
            ),
            openapi.Parameter(
                'is_active', openapi.IN_QUERY, description="Filter by active status", 
                type=openapi.TYPE_BOOLEAN, required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="Quizzes retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                            'difficulty': openapi.Schema(type=openapi.TYPE_STRING),
                            'time_limit': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'passing_score': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            'created_by': openapi.Schema(type=openapi.TYPE_STRING),
                            'total_attempts': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'average_score': openapi.Schema(type=openapi.TYPE_NUMBER),
                            'completion_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                        }
                    )
                )
            ),
            403: openapi.Response(description="Access denied - Admin only"),
        }
    )
    def get(self, request):
        """
        Get all quizzes with admin statistics.
        """
        # Get query parameters
        category = request.query_params.get('category')
        difficulty = request.query_params.get('difficulty')
        is_active = request.query_params.get('is_active')
        
        # Start with all quizzes
        quizzes = Quiz.objects.select_related('created_by').prefetch_related('categories').all()
        
        # Apply filters
        if category:
            quizzes = quizzes.filter(categories__name__icontains=category)
        
        if difficulty:
            quizzes = quizzes.filter(difficulty=difficulty)
        
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            quizzes = quizzes.filter(is_active=is_active_bool)
        
        # Prepare response data
        quiz_data = []
        for quiz in quizzes:
            # Get quiz statistics
            attempts = quiz.attempts.all()
            total_attempts = attempts.count()
            completed_attempts = attempts.filter(completed_at__isnull=False).count()
            avg_score = attempts.filter(completed_at__isnull=False).aggregate(
                avg_score=Avg('score')
            )['avg_score']
            
            completion_rate = (completed_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            quiz_data.append({
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'difficulty': quiz.difficulty,
                'time_limit': quiz.time_limit,
                'passing_score': quiz.passing_score,
                'is_active': quiz.is_active,
                'created_by': quiz.created_by.username,
                'categories': [cat.name for cat in quiz.categories.all()],
                'total_attempts': total_attempts,
                'average_score': float(avg_score) if avg_score else 0,
                'completion_rate': round(completion_rate, 2),
            })
        
        return Response(quiz_data, status=status.HTTP_200_OK)


class AdminQuizDetailView(APIView):
    """
    GET /api/v1/admin/quizzes/{quiz_id}/ endpoint to get detailed quiz information.
    """
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get detailed quiz information with comprehensive statistics",
        manual_parameters=[
            openapi.Parameter(
                'quiz_id', openapi.IN_PATH, description="Quiz ID", 
                type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Quiz details retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                        'description': openapi.Schema(type=openapi.TYPE_STRING),
                        'difficulty': openapi.Schema(type=openapi.TYPE_STRING),
                        'time_limit': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'passing_score': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'created_by': openapi.Schema(type=openapi.TYPE_STRING),
                        'categories': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                        'questions_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_attempts': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'completed_attempts': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'average_score': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'pass_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'average_time_taken': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'recent_attempts': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'user': openapi.Schema(type=openapi.TYPE_STRING),
                                    'score': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'completed_at': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                )
            ),
            404: openapi.Response(description="Quiz not found"),
            403: openapi.Response(description="Access denied - Admin only"),
        }
    )
    def get(self, request, quiz_id):
        """
        Get detailed quiz information with comprehensive statistics.
        """
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Get comprehensive quiz statistics
        attempts = quiz.attempts.all()
        total_attempts = attempts.count()
        completed_attempts = attempts.filter(completed_at__isnull=False)
        passed_attempts = completed_attempts.filter(is_passed=True)
        
        # Calculate statistics
        avg_score = completed_attempts.aggregate(avg_score=Avg('score'))['avg_score']
        pass_rate = (passed_attempts.count() / completed_attempts.count() * 100) if completed_attempts.count() > 0 else 0
        avg_time = completed_attempts.aggregate(avg_time=Avg('time_taken'))['avg_time']
        
        # Get recent attempts
        recent_attempts = completed_attempts.order_by('-completed_at')[:10]
        recent_attempts_data = []
        for attempt in recent_attempts:
            recent_attempts_data.append({
                'user': attempt.user.username,
                'score': float(attempt.score) if attempt.score else 0,
                'completed_at': attempt.completed_at.isoformat(),
            })
        
        quiz_data = {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'difficulty': quiz.difficulty,
            'time_limit': quiz.time_limit,
            'passing_score': quiz.passing_score,
            'is_active': quiz.is_active,
            'created_by': quiz.created_by.username,
            'categories': [cat.name for cat in quiz.categories.all()],
            'questions_count': quiz.questions.count(),
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts.count(),
            'average_score': float(avg_score) if avg_score else 0,
            'pass_rate': round(pass_rate, 2),
            'average_time_taken': float(avg_time) if avg_time else 0,
            'recent_attempts': recent_attempts_data,
        }
        
        return Response(quiz_data, status=status.HTTP_200_OK)


class AdminSystemAnalyticsView(APIView):
    """
    GET /api/v1/admin/analytics/ endpoint to get system-wide analytics.
    """
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get comprehensive system-wide analytics and statistics",
        manual_parameters=[
            openapi.Parameter(
                'period', openapi.IN_QUERY, description="Time period for analytics", 
                type=openapi.TYPE_STRING, required=False,
                enum=['today', 'week', 'month', 'all']
            ),
        ],
        responses={
            200: openapi.Response(
                description="System analytics retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_users': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_quizzes': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_attempts': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'active_users_today': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'quizzes_created_today': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'attempts_today': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'average_score_system': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'completion_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'user_roles_distribution': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'students': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'teachers': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'admins': openapi.Schema(type=openapi.TYPE_INTEGER),
                            }
                        ),
                        'popular_quizzes': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                                    'attempts_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'average_score': openapi.Schema(type=openapi.TYPE_NUMBER),
                                }
                            )
                        ),
                        'recent_activity': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'user': openapi.Schema(type=openapi.TYPE_STRING),
                                    'action': openapi.Schema(type=openapi.TYPE_STRING),
                                    'timestamp': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                )
            ),
            403: openapi.Response(description="Access denied - Admin only"),
        }
    )
    def get(self, request):
        """
        Get comprehensive system-wide analytics.
        """
        period = request.query_params.get('period', 'all')
        
        # Calculate time filter
        if period == 'today':
            time_filter = timezone.now().date()
        elif period == 'week':
            time_filter = timezone.now() - timedelta(days=7)
        elif period == 'month':
            time_filter = timezone.now() - timedelta(days=30)
        else:
            time_filter = None
        
        # Basic counts
        total_users = User.objects.count()
        total_quizzes = Quiz.objects.count()
        total_attempts = QuizAttempt.objects.count()
        
        # Today's activity
        today = timezone.now().date()
        active_users_today = QuizAttempt.objects.filter(
            started_at__date=today
        ).values('user').distinct().count()
        
        quizzes_created_today = Quiz.objects.filter(
            created_at__date=today
        ).count()
        
        attempts_today = QuizAttempt.objects.filter(
            started_at__date=today
        ).count()
        
        # System averages
        completed_attempts = QuizAttempt.objects.filter(completed_at__isnull=False)
        if time_filter:
            completed_attempts = completed_attempts.filter(completed_at__gte=time_filter)
        
        avg_score_system = completed_attempts.aggregate(avg_score=Avg('score'))['avg_score']
        completion_rate = (completed_attempts.count() / total_attempts * 100) if total_attempts > 0 else 0
        
        # User roles distribution
        user_roles = UserProfile.objects.values('role').annotate(count=Count('role'))
        roles_distribution = {
            'students': 0,
            'teachers': 0,
            'admins': 0
        }
        for role_data in user_roles:
            roles_distribution[role_data['role']] = role_data['count']
        
        # Popular quizzes
        popular_quizzes = Quiz.objects.annotate(
            attempts_count=Count('attempts')
        ).order_by('-attempts_count')[:5]
        
        popular_quizzes_data = []
        for quiz in popular_quizzes:
            avg_score = quiz.attempts.filter(completed_at__isnull=False).aggregate(
                avg_score=Avg('score')
            )['avg_score']
            popular_quizzes_data.append({
                'title': quiz.title,
                'attempts_count': quiz.attempts_count,
                'average_score': float(avg_score) if avg_score else 0,
            })
        
        # Recent activity (last 10 completed attempts)
        recent_activity = QuizAttempt.objects.filter(
            completed_at__isnull=False
        ).order_by('-completed_at')[:10]
        
        recent_activity_data = []
        for attempt in recent_activity:
            recent_activity_data.append({
                'user': attempt.user.username,
                'action': f"Completed {attempt.quiz.title}",
                'timestamp': attempt.completed_at.isoformat(),
            })
        
        analytics_data = {
            'total_users': total_users,
            'total_quizzes': total_quizzes,
            'total_attempts': total_attempts,
            'active_users_today': active_users_today,
            'quizzes_created_today': quizzes_created_today,
            'attempts_today': attempts_today,
            'average_score_system': float(avg_score_system) if avg_score_system else 0,
            'completion_rate': round(completion_rate, 2),
            'user_roles_distribution': roles_distribution,
            'popular_quizzes': popular_quizzes_data,
            'recent_activity': recent_activity_data,
        }
        
        return Response(analytics_data, status=status.HTTP_200_OK)


class AdminCategoryListView(APIView):
    """
    GET /api/v1/admin/categories/ endpoint to list all categories with statistics.
    """
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get list of all categories with quiz statistics",
        responses={
            200: openapi.Response(
                description="Categories retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                            'quizzes_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'total_attempts': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'average_score': openapi.Schema(type=openapi.TYPE_NUMBER),
                        }
                    )
                )
            ),
            403: openapi.Response(description="Access denied - Admin only"),
        }
    )
    def get(self, request):
        """
        Get all categories with quiz statistics.
        """
        categories = Category.objects.annotate(
            quizzes_count=Count('quizzes')
        ).all()
        
        category_data = []
        for category in categories:
            # Get statistics for quizzes in this category
            category_quizzes = category.quizzes.all()
            total_attempts = QuizAttempt.objects.filter(quiz__in=category_quizzes).count()
            avg_score = QuizAttempt.objects.filter(
                quiz__in=category_quizzes,
                completed_at__isnull=False
            ).aggregate(avg_score=Avg('score'))['avg_score']
            
            category_data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'quizzes_count': category.quizzes_count,
                'total_attempts': total_attempts,
                'average_score': float(avg_score) if avg_score else 0,
            })
        
        return Response(category_data, status=status.HTTP_200_OK) 