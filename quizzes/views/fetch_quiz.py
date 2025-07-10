"""
Quiz fetching views for EduPulse project.

This module contains views for fetching quiz data and user progress.
Dev 2 responsibility: Quiz Logic
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import Quiz, Question, QuizAttempt
from ..serializers import QuizSerializer, QuestionSerializer, QuizAttemptSerializer
from common.permissions import IsStudentOrReadOnly, HasQuizAccess
from common.utils import calculate_quiz_statistics, format_time_duration


class QuizListView(APIView):
    """
    GET /quiz/ endpoint to fetch all active quizzes.
    """
    permission_classes = [IsStudentOrReadOnly]

    @swagger_auto_schema(
        operation_description="Get list of all active quizzes",
        responses={
            200: openapi.Response(
                description="List of quizzes retrieved successfully",
                schema=QuizSerializer(many=True)
            ),
            401: openapi.Response(description="Authentication required"),
        }
    )
    def get(self, request):
        """
        Get all active quizzes with optional filtering.
        """
        # Get query parameters for filtering
        difficulty = request.query_params.get('difficulty')
        category = request.query_params.get('category')
        
        quizzes = Quiz.objects.filter(is_active=True)
        
        # Apply filters
        if difficulty:
            quizzes = quizzes.filter(difficulty=difficulty)
        if category:
            quizzes = quizzes.filter(categories__name__icontains=category)
        
        # Add statistics for each quiz
        quiz_data = []
        for quiz in quizzes:
            quiz_serializer = QuizSerializer(quiz)
            quiz_dict = quiz_serializer.data
            
            # Add quiz statistics
            stats = calculate_quiz_statistics(quiz.id)
            quiz_dict.update(stats)
            
            quiz_data.append(quiz_dict)
        
        return Response(quiz_data, status=status.HTTP_200_OK)


class QuizDetailView(APIView):
    """
    GET /quiz/<int:pk>/ endpoint to fetch a specific quiz.
    """
    permission_classes = [HasQuizAccess]

    @swagger_auto_schema(
        operation_description="Get detailed information about a specific quiz",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH, description="Quiz ID", type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Quiz details retrieved successfully",
                schema=QuizSerializer()
            ),
            404: openapi.Response(description="Quiz not found"),
            403: openapi.Response(description="Access denied"),
        }
    )
    def get(self, request, pk):
        """
        Get detailed information about a specific quiz.
        """
        quiz = get_object_or_404(Quiz, pk=pk, is_active=True)
        
        # Check if user has access to this quiz
        from common.permissions import HasQuizAccess
        quiz_access = HasQuizAccess()
        if not quiz_access.has_object_permission(request, self, quiz):
            return Response(
                {"detail": "You don't have access to this quiz"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = QuizSerializer(quiz)
        quiz_data = serializer.data
        
        # Add quiz statistics
        stats = calculate_quiz_statistics(quiz.id)
        quiz_data.update(stats)
        
        return Response(quiz_data, status=status.HTTP_200_OK)


class StartQuizView(APIView):
    """
    POST /quiz/<int:quiz_id>/start/ endpoint to start a quiz attempt.
    """
    permission_classes = [HasQuizAccess]

    @swagger_auto_schema(
        operation_description="Start a new quiz attempt",
        manual_parameters=[
            openapi.Parameter(
                'quiz_id', openapi.IN_PATH, description="Quiz ID", type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            201: openapi.Response(
                description="Quiz attempt started successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'quiz_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'started_at': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description="Cannot start quiz"),
            403: openapi.Response(description="Access denied"),
        }
    )
    def post(self, request, quiz_id):
        """
        Start a new quiz attempt.
        """
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        
        # Check if user has access to this quiz
        from common.permissions import HasQuizAccess
        quiz_access = HasQuizAccess()
        if not quiz_access.has_object_permission(request, self, quiz):
            return Response(
                {"detail": "You don't have access to this quiz"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user already has an active attempt
        existing_attempt = QuizAttempt.objects.filter(
            user=request.user,
            quiz=quiz,
            completed_at__isnull=True
        ).first()
        
        if existing_attempt:
            return Response({
                "message": "You already have an active attempt for this quiz",
                "attempt_id": existing_attempt.id
            }, status=status.HTTP_200_OK)
        
        # Create new attempt
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            started_at=timezone.now()
        )
        
        return Response({
            "message": "Quiz attempt started successfully",
            "attempt_id": attempt.id,
            "quiz_id": quiz.id,
            "started_at": attempt.started_at.isoformat()
        }, status=status.HTTP_201_CREATED)


class QuizQuestionsView(APIView):
    """
    GET /quiz/<int:quiz_id>/questions/ endpoint to fetch all questions for a specific quiz.
    """
    permission_classes = [HasQuizAccess]

    @swagger_auto_schema(
        operation_description="Get all questions for a specific quiz",
        manual_parameters=[
            openapi.Parameter(
                'quiz_id', openapi.IN_PATH, description="Quiz ID", type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Questions retrieved successfully",
                schema=QuestionSerializer(many=True)
            ),
            404: openapi.Response(description="Quiz not found"),
            403: openapi.Response(description="Access denied"),
        }
    )
    def get(self, request, quiz_id):
        """
        Get all questions for a specific quiz.
        """
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        
        # Check if user has access to this quiz
        from common.permissions import HasQuizAccess
        quiz_access = HasQuizAccess()
        if not quiz_access.has_object_permission(request, self, quiz):
            return Response(
                {"detail": "You don't have access to this quiz"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        questions = quiz.questions.all().order_by('order')
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuizQuestionDetailView(APIView):
    """
    GET /quiz/<int:quiz_id>/questions/<int:question_id>/ endpoint to fetch a specific question from a quiz.
    """
    permission_classes = [HasQuizAccess]

    @swagger_auto_schema(
        operation_description="Get a specific question from a quiz",
        manual_parameters=[
            openapi.Parameter(
                'quiz_id', openapi.IN_PATH, description="Quiz ID", type=openapi.TYPE_INTEGER, required=True
            ),
            openapi.Parameter(
                'question_id', openapi.IN_PATH, description="Question ID", type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Question retrieved successfully",
                schema=QuestionSerializer()
            ),
            404: openapi.Response(description="Quiz or question not found"),
            403: openapi.Response(description="Access denied"),
        }
    )
    def get(self, request, quiz_id, question_id):
        """
        Get a specific question from a quiz.
        """
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        question = get_object_or_404(quiz.questions, pk=question_id)
        
        # Check if user has access to this quiz
        from common.permissions import HasQuizAccess
        quiz_access = HasQuizAccess()
        if not quiz_access.has_object_permission(request, self, quiz):
            return Response(
                {"detail": "You don't have access to this quiz"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuizProgressView(APIView):
    """
    GET /quiz/<int:quiz_id>/progress/ endpoint to get user's progress on a specific quiz.
    """
    permission_classes = [HasQuizAccess]

    @swagger_auto_schema(
        operation_description="Get user's progress on a specific quiz",
        manual_parameters=[
            openapi.Parameter(
                'quiz_id', openapi.IN_PATH, description="Quiz ID", type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Progress retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'quiz_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'quiz_title': openapi.Schema(type=openapi.TYPE_STRING),
                        'progress': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'completed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'score': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'time_taken': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            404: openapi.Response(description="Quiz not found"),
            403: openapi.Response(description="Access denied"),
        }
    )
    def get(self, request, quiz_id):
        """
        Get user's progress on a specific quiz.
        """
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        
        # Check if user has access to this quiz
        from common.permissions import HasQuizAccess
        quiz_access = HasQuizAccess()
        if not quiz_access.has_object_permission(request, self, quiz):
            return Response(
                {"detail": "You don't have access to this quiz"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).first()

        if not attempt:
            return Response({
                "quiz_id": quiz.id,
                "quiz_title": quiz.title,
                "progress": 0,
                "completed": False,
                "score": None,
                "time_taken": None
            }, status=status.HTTP_200_OK)

        total_questions = quiz.questions.count()
        answered_questions = attempt.responses.count()
        progress = round((answered_questions / total_questions) * 100, 2) if total_questions > 0 else 0
        
        # Calculate time taken if completed
        time_taken = None
        if attempt.completed_at and attempt.started_at:
            time_taken = format_time_duration(
                int((attempt.completed_at - attempt.started_at).total_seconds())
            )

        return Response({
            "quiz_id": quiz.id,
            "quiz_title": quiz.title,
            "progress": progress,
            "completed": attempt.completed_at is not None,
            "score": attempt.score,
            "time_taken": time_taken
        }, status=status.HTTP_200_OK)


class UserQuizAttemptsView(APIView):
    """
    GET /quiz/attempts/ endpoint to get list of user's quiz attempts.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get list of user's quiz attempts",
        responses={
            200: openapi.Response(
                description="Quiz attempts retrieved successfully",
                schema=QuizAttemptSerializer(many=True)
            ),
            401: openapi.Response(description="Authentication required"),
        }
    )
    def get(self, request):
        """
        Get list of user's quiz attempts with optional filtering.
        """
        # Get query parameters for filtering
        status_filter = request.query_params.get('status')  # 'completed', 'in_progress'
        
        attempts = QuizAttempt.objects.filter(user=request.user)
        
        # Apply filters
        if status_filter == 'completed':
            attempts = attempts.filter(completed_at__isnull=False)
        elif status_filter == 'in_progress':
            attempts = attempts.filter(completed_at__isnull=True)
        
        # Order by most recent first
        attempts = attempts.order_by('-started_at')
        
        serializer = QuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
