# quizzes/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Quiz, Question, QuizAttempt
from ..serializers import QuizSerializer, QuestionSerializer, QuizAttemptSerializer
from common.permissions import HasQuizAccess


class QuizListView(APIView):
    """
    GET /quiz/ endpoint to fetch all active quizzes.
    """
    permission_classes = [IsAuthenticated, HasQuizAccess]

    def get(self, request):
        quizzes = Quiz.objects.filter(is_active=True)
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuizDetailView(APIView):
    """
    GET /quiz/<int:pk>/ endpoint to fetch a specific quiz.
    """
    permission_classes = [IsAuthenticated, HasQuizAccess]

    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk, is_active=True)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuizQuestionsView(APIView):
    """
    GET /quiz/<int:quiz_id>/questions/ endpoint to fetch all questions for a specific quiz.
    """
    permission_classes = [IsAuthenticated, HasQuizAccess]

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        questions = quiz.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuizQuestionDetailView(APIView):
    """
    GET /quiz/<int:quiz_id>/questions/<int:question_id>/ endpoint to fetch a specific question from a quiz.
    """
    permission_classes = [IsAuthenticated, HasQuizAccess]

    def get(self, request, quiz_id, question_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        question = get_object_or_404(quiz.questions, pk=question_id)
        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuizProgressView(APIView):
    """
    GET /quiz/<int:quiz_id>/progress/ endpoint to get user's progress on a specific quiz.
    """
    permission_classes = [IsAuthenticated, HasQuizAccess]

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).first()

        if not attempt:
            return Response({
                "quiz_id": quiz.id,
                "quiz_title": quiz.title,
                "progress": 0,
                "completed": False
            }, status=status.HTTP_200_OK)

        total_questions = quiz.questions.count()
        answered_questions = attempt.responses.count()
        progress = round((answered_questions / total_questions) * 100, 2) if total_questions > 0 else 0

        return Response({
            "quiz_id": quiz.id,
            "quiz_title": quiz.title,
            "progress": progress,
            "completed": attempt.completed_at is not None,
            "score": attempt.score
        }, status=status.HTTP_200_OK)


class UserQuizAttemptsView(APIView):
    """
    GET /quiz/attempts/ endpoint to get list of user's quiz attempts.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        attempts = QuizAttempt.objects.filter(user=request.user)
        serializer = QuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
