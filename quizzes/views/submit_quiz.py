"""
Quiz submission views for EduPulse project.

This module contains views for submitting quiz answers and managing quiz attempts.
Dev 2 responsibility: Quiz Logic
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import Quiz, Question, Choice, QuizAttempt, QuizResponse
from ..serializers import (
    QuizSerializer, QuestionSerializer, QuizAttemptSerializer
)
from common.permissions import CanSubmitQuiz, HasQuizAccess
from common.utils import (
    calculate_score, validate_quiz_submission, 
    format_time_duration, sanitize_user_input
)


class SubmitQuizView(APIView):
    """
    POST /quiz/<int:quiz_id>/submit/
    Submit quiz answers and calculate results.
    """
    permission_classes = [CanSubmitQuiz]

    @swagger_auto_schema(
        operation_description="Submit quiz answers and calculate results",
        manual_parameters=[
            openapi.Parameter(
                'quiz_id', openapi.IN_PATH, description="Quiz ID", type=openapi.TYPE_INTEGER, required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'answers': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'question_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'selected_choice_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
                            'text_answer': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                ),
                'feedback': openapi.Schema(type=openapi.TYPE_STRING),
                'user_difficulty_rating': openapi.Schema(type=openapi.TYPE_STRING, enum=['easy', 'medium', 'hard']),
            }
        ),
        responses={
            200: openapi.Response(
                description="Quiz submitted successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'score': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'is_passed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'time_taken': openapi.Schema(type=openapi.TYPE_STRING),
                        'correct_answers': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            400: openapi.Response(description="Invalid submission data"),
            403: openapi.Response(description="Cannot submit quiz"),
            404: openapi.Response(description="Quiz not found"),
        }
    )
    @transaction.atomic
    def post(self, request, quiz_id):
        """
        Submit quiz answers and calculate results.
        """
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        data = request.data
        answers = data.get('answers', [])
        
        # Validate submission using utility function
        validation_result = validate_quiz_submission(answers, quiz_id, request.user.id)
        if not validation_result['valid']:
            return Response({
                'message': 'Quiz submission validation failed',
                'errors': validation_result['errors']
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get or create attempt
        attempt, created = QuizAttempt.objects.get_or_create(
            user=request.user,
            quiz=quiz,
            defaults={'is_passed': False}
        )

        # Calculate time taken
        time_taken_seconds = 0
        if attempt.started_at:
            time_taken_seconds = int((timezone.now() - attempt.started_at).total_seconds())

        total_points = 0
        points_earned = 0
        correct_answers = 0
        total_questions = quiz.questions.count()

        # Process each answer
        for ans in answers:
            question_id = ans.get('question_id')
            selected_choice_ids = ans.get('selected_choice_ids', [])
            text_answer = sanitize_user_input(ans.get('text_answer', ''))

            question = get_object_or_404(quiz.questions, pk=question_id)
            total_points += question.points

            response, created = QuizResponse.objects.get_or_create(
                attempt=attempt,
                question=question,
                defaults={'text_answer': text_answer}
            )

            if selected_choice_ids:
                selected_choices = Choice.objects.filter(pk__in=selected_choice_ids, question=question)
                response.selected_choices.set(selected_choices)

                correct_choices = question.choices.filter(is_correct=True)
                is_correct = set(selected_choices) == set(correct_choices)
                response.is_correct = is_correct
            elif question.question_type in ['short_answer', 'essay']:
                response.is_correct = None  # Would need manual grading
            else:
                response.is_correct = None

            if response.is_correct:
                response.points_earned = question.points
                points_earned += question.points
                correct_answers += 1
            else:
                response.points_earned = 0

            response.save()

        # Calculate score using utility function
        score = calculate_score(
            correct_answers=correct_answers,
            total_questions=total_questions,
            time_taken=time_taken_seconds,
            time_limit=quiz.time_limit,
            difficulty_bonus=1.0  # Could be based on quiz difficulty
        )

        # Update attempt
        attempt.score = score
        attempt.is_passed = score >= quiz.passing_score
        attempt.completed_at = timezone.now()
        attempt.time_taken = time_taken_seconds
        
        # Add optional feedback and difficulty rating
        if 'feedback' in data:
            attempt.feedback = sanitize_user_input(data['feedback'])
        if 'user_difficulty_rating' in data:
            attempt.user_difficulty_rating = data['user_difficulty_rating']
        
        attempt.save()

        return Response({
            "message": "Quiz submitted successfully.",
            "score": score,
            "is_passed": attempt.is_passed,
            "time_taken": format_time_duration(time_taken_seconds),
            "correct_answers": correct_answers,
            "total_questions": total_questions
        }, status=status.HTTP_200_OK)


class QuizResultView(APIView):
    """
    GET /quiz/<int:quiz_id>/result/
    Get user's result for a specific quiz.
    """
    permission_classes = [HasQuizAccess]

    @swagger_auto_schema(
        operation_description="Get user's result for a specific quiz",
        manual_parameters=[
            openapi.Parameter(
                'quiz_id', openapi.IN_PATH, description="Quiz ID", type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Quiz result retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'quiz_title': openapi.Schema(type=openapi.TYPE_STRING),
                        'score': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'is_passed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'completed_at': openapi.Schema(type=openapi.TYPE_STRING),
                        'time_taken': openapi.Schema(type=openapi.TYPE_STRING),
                        'correct_answers': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            404: openapi.Response(description="No attempt found for this quiz"),
            403: openapi.Response(description="Access denied"),
        }
    )
    def get(self, request, quiz_id):
        """
        Get user's result for a specific quiz.
        """
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        
        # Check if user has access to this quiz
        quiz_access = HasQuizAccess()
        if not quiz_access.has_object_permission(request, self, quiz):
            return Response(
                {"detail": "You don't have access to this quiz"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).first()

        if not attempt:
            return Response(
                {"detail": "No attempt found for this quiz."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Calculate time taken
        time_taken = None
        if attempt.completed_at and attempt.started_at:
            time_taken = format_time_duration(
                int((attempt.completed_at - attempt.started_at).total_seconds())
            )

        # Get correct answers count
        correct_answers = attempt.responses.filter(is_correct=True).count()
        total_questions = quiz.questions.count()

        return Response({
            "quiz_title": quiz.title,
            "score": attempt.score,
            "is_passed": attempt.is_passed,
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
            "time_taken": time_taken,
            "correct_answers": correct_answers,
            "total_questions": total_questions
        }, status=status.HTTP_200_OK)


class SaveAnswerView(APIView):
    """
    POST /quiz/<int:quiz_id>/questions/<int:question_id>/answer/
    Save answer for a specific question.
    """
    permission_classes = [CanSubmitQuiz]

    @swagger_auto_schema(
        operation_description="Save answer for a specific question",
        manual_parameters=[
            openapi.Parameter(
                'quiz_id', openapi.IN_PATH, description="Quiz ID", type=openapi.TYPE_INTEGER, required=True
            ),
            openapi.Parameter(
                'question_id', openapi.IN_PATH, description="Question ID", type=openapi.TYPE_INTEGER, required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'selected_choice_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
                'text_answer': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description="Answer saved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'saved_at': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description="Invalid answer data"),
            403: openapi.Response(description="Cannot save answer"),
            404: openapi.Response(description="Quiz or question not found"),
        }
    )
    @transaction.atomic
    def post(self, request, quiz_id, question_id):
        """
        Save answer for a specific question.
        """
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        question = get_object_or_404(quiz.questions, pk=question_id)

        attempt, created = QuizAttempt.objects.get_or_create(
            user=request.user,
            quiz=quiz,
            defaults={'is_passed': False}
        )

        selected_choice_ids = request.data.get('selected_choice_ids', [])
        text_answer = sanitize_user_input(request.data.get('text_answer', ''))

        response, created = QuizResponse.objects.get_or_create(
            attempt=attempt,
            question=question,
            defaults={'text_answer': text_answer}
        )

        if selected_choice_ids:
            selected_choices = Choice.objects.filter(pk__in=selected_choice_ids, question=question)
            response.selected_choices.set(selected_choices)

            correct_choices = question.choices.filter(is_correct=True)
            is_correct = set(selected_choices) == set(correct_choices)
            response.is_correct = is_correct
        elif question.question_type in ['short_answer', 'essay']:
            response.is_correct = None
        else:
            response.is_correct = None

        response.save()

        return Response({
            "message": "Answer saved successfully.",
            "saved_at": response.answered_at.isoformat()
        }, status=status.HTTP_200_OK)


class QuizFeedbackView(APIView):
    """
    GET /quiz/<int:quiz_id>/feedback/
    Get detailed feedback for completed quiz.
    """
    permission_classes = [HasQuizAccess]

    @swagger_auto_schema(
        operation_description="Get detailed feedback for completed quiz",
        manual_parameters=[
            openapi.Parameter(
                'quiz_id', openapi.IN_PATH, description="Quiz ID", type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Feedback retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'quiz_title': openapi.Schema(type=openapi.TYPE_STRING),
                        'score': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'feedback': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'question': openapi.Schema(type=openapi.TYPE_STRING),
                                    'selected_choices': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                                    'text_answer': openapi.Schema(type=openapi.TYPE_STRING),
                                    'is_correct': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    'explanation': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                )
            ),
            404: openapi.Response(description="No attempt found"),
            403: openapi.Response(description="Access denied"),
        }
    )
    def get(self, request, quiz_id):
        """
        Get detailed feedback for completed quiz.
        """
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        
        # Check if user has access to this quiz
        quiz_access = HasQuizAccess()
        if not quiz_access.has_object_permission(request, self, quiz):
            return Response(
                {"detail": "You don't have access to this quiz"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).first()

        if not attempt:
            return Response(
                {"detail": "No attempt found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        feedback = []
        for response in attempt.responses.all():
            feedback.append({
                "question": response.question.question_text,
                "selected_choices": [choice.choice_text for choice in response.selected_choices.all()],
                "text_answer": response.text_answer,
                "is_correct": response.is_correct,
                "explanation": response.question.explanation
            })

        return Response({
            "quiz_title": quiz.title,
            "score": attempt.score,
            "feedback": feedback
        }, status=status.HTTP_200_OK)


class RetakeQuizView(APIView):
    """
    POST /quiz/<int:quiz_id>/retake/
    Start a new attempt for a previously taken quiz.
    """
    permission_classes = [HasQuizAccess]

    @swagger_auto_schema(
        operation_description="Start a new attempt for a previously taken quiz",
        manual_parameters=[
            openapi.Parameter(
                'quiz_id', openapi.IN_PATH, description="Quiz ID", type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            201: openapi.Response(
                description="New quiz attempt started",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'quiz_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'started_at': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            403: openapi.Response(description="Cannot retake quiz"),
            404: openapi.Response(description="Quiz not found"),
        }
    )
    def post(self, request, quiz_id):
        """
        Start a new attempt for a previously taken quiz.
        """
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        
        # Delete previous attempts
        QuizAttempt.objects.filter(user=request.user, quiz=quiz).delete()
        
        # Create new attempt
        attempt = QuizAttempt.objects.create(
            user=request.user, 
            quiz=quiz,
            started_at=timezone.now()
        )

        return Response({
            "message": "New quiz attempt started.",
            "quiz_id": quiz.id,
            "attempt_id": attempt.id,
            "started_at": attempt.started_at.isoformat()
        }, status=status.HTTP_201_CREATED)


class QuizAnalyticsView(APIView):
    """
    GET /quiz/<int:quiz_id>/analytics/
    Get analytics for a specific quiz.
    """
    permission_classes = [HasQuizAccess]

    @swagger_auto_schema(
        operation_description="Get analytics for a specific quiz",
        manual_parameters=[
            openapi.Parameter(
                'quiz_id', openapi.IN_PATH, description="Quiz ID", type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Analytics retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'quiz_title': openapi.Schema(type=openapi.TYPE_STRING),
                        'total_attempts': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'average_score': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'completion_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'user_attempt': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            403: openapi.Response(description="Access denied"),
            404: openapi.Response(description="Quiz not found"),
        }
    )
    def get(self, request, quiz_id):
        """
        Get analytics for a specific quiz.
        """
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        
        # Check if user has access to this quiz
        quiz_access = HasQuizAccess()
        if not quiz_access.has_object_permission(request, self, quiz):
            return Response(
                {"detail": "You don't have access to this quiz"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get quiz statistics using utility function
        from common.utils import calculate_quiz_statistics
        stats = calculate_quiz_statistics(quiz.id)
        
        # Get user's attempt
        user_attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).first()
        user_attempt_data = None
        if user_attempt:
            user_attempt_data = {
                "score": user_attempt.score,
                "is_passed": user_attempt.is_passed,
                "completed_at": user_attempt.completed_at.isoformat() if user_attempt.completed_at else None,
                "time_taken": format_time_duration(user_attempt.time_taken) if user_attempt.time_taken else None
            }
        
        return Response({
            "quiz_title": quiz.title,
            **stats,
            "user_attempt": user_attempt_data
        }, status=status.HTTP_200_OK)
