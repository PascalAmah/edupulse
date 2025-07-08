# quizzes/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from ..models import Quiz, Question, Choice, QuizAttempt, QuizResponse
from ..serializers import (
    QuizSerializer, QuestionSerializer, QuizAttemptSerializer
)
from common.permissions import CanSubmitQuiz


class SubmitQuizView(APIView):
    """
    POST /quiz/<int:quiz_id>/submit/
    Submit quiz answers and calculate results.
    """
    permission_classes = [IsAuthenticated, CanSubmitQuiz]

    @transaction.atomic
    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        data = request.data
        answers = data.get('answers', [])

        attempt, created = QuizAttempt.objects.get_or_create(
            user=request.user,
            quiz=quiz,
            defaults={'is_passed': False}
        )

        total_points = 0
        points_earned = 0

        for ans in answers:
            question_id = ans.get('question_id')
            selected_choice_ids = ans.get('selected_choice_ids', [])
            text_answer = ans.get('text_answer', '')

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
            elif question.question_type == 'short_answer':
                response.is_correct = None
            else:
                response.is_correct = None

            if response.is_correct:
                response.points_earned = question.points
                points_earned += question.points
            else:
                response.points_earned = 0

            response.save()

        percentage = round((points_earned / total_points) * 100, 2) if total_points > 0 else 0
        attempt.score = percentage
        attempt.is_passed = percentage >= quiz.passing_score
        attempt.completed_at = timezone.now()
        attempt.save()

        return Response({
            "message": "Quiz submitted successfully.",
            "score": percentage,
            "is_passed": attempt.is_passed
        }, status=status.HTTP_200_OK)


class QuizResultView(APIView):
    """
    GET /quiz/<int:quiz_id>/result/
    Get user's result for a specific quiz.
    """
    permission_classes = [IsAuthenticated, CanSubmitQuiz]

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).first()

        if not attempt:
            return Response({"detail": "No attempt found for this quiz."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "quiz_title": quiz.title,
            "score": attempt.score,
            "is_passed": attempt.is_passed,
            "completed_at": attempt.completed_at
        }, status=status.HTTP_200_OK)


class SaveAnswerView(APIView):
    """
    POST /quiz/<int:quiz_id>/questions/<int:question_id>/answer/
    Save answer for a specific question.
    """
    permission_classes = [IsAuthenticated, CanSubmitQuiz]

    @transaction.atomic
    def post(self, request, quiz_id, question_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        question = get_object_or_404(quiz.questions, pk=question_id)

        attempt, created = QuizAttempt.objects.get_or_create(
            user=request.user,
            quiz=quiz,
            defaults={'is_passed': False}
        )

        selected_choice_ids = request.data.get('selected_choice_ids', [])
        text_answer = request.data.get('text_answer', '')

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
        elif question.question_type == 'short_answer':
            response.is_correct = None
        else:
            response.is_correct = None

        response.save()

        return Response({"message": "Answer saved successfully."}, status=status.HTTP_200_OK)


class QuizFeedbackView(APIView):
    """
    GET /quiz/<int:quiz_id>/feedback/
    Get detailed feedback for completed quiz.
    """
    permission_classes = [IsAuthenticated, CanSubmitQuiz]

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).first()

        if not attempt:
            return Response({"detail": "No attempt found."}, status=status.HTTP_404_NOT_FOUND)

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
    permission_classes = [IsAuthenticated, CanSubmitQuiz]

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        QuizAttempt.objects.filter(user=request.user, quiz=quiz).delete()
        attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz)

        return Response({
            "message": "New quiz attempt started.",
            "quiz_id": quiz.id,
            "attempt_id": attempt.id
        }, status=status.HTTP_201_CREATED)


from django.db.models import Avg

class QuizAnalyticsView(APIView):
    """
    GET /quiz/<int:quiz_id>/analytics/
    Get analytics for a specific quiz.
    """
    permission_classes = [IsAuthenticated, CanSubmitQuiz]

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
        avg_score = quiz.attempts.aggregate(Avg('score'))['score__avg']
        total_attempts = quiz.attempts.count()
        completed_attempts = quiz.attempts.filter(completed_at__isnull=False).count()
        completion_rate = round((completed_attempts / total_attempts) * 100, 2) if total_attempts > 0 else 0

        difficult_questions = []
        for question in quiz.questions.all():
            total_responses = question.responses.count()
            correct_responses = question.responses.filter(is_correct=True).count()
            if total_responses > 0:
                correct_rate = round((correct_responses / total_responses) * 100, 2)
                if correct_rate < 50:
                    difficult_questions.append({
                        "question_text": question.question_text,
                        "correct_rate": correct_rate
                    })

        return Response({
            "quiz_title": quiz.title,
            "average_score": avg_score,
            "completion_rate": completion_rate,
            "difficult_questions": difficult_questions
        }, status=status.HTTP_200_OK)
