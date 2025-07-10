"""
Progress tracking views for EduPulse project.

This module contains views for learning progress tracking.
Dev 3 responsibility: Mood, Progress, Gamification
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from ..models import LearningProgress, DailyGoal, LearningSession
from ..serializers import LearningProgressSerializer, DailyGoalSerializer, LearningSessionSerializer
from django.db.models import Avg, Sum


class ProgressOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            progress = LearningProgress.objects.get(user=user)
            serializer = LearningProgressSerializer(progress)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except LearningProgress.DoesNotExist:
            return Response({'message': 'Progress not found.'}, status=status.HTTP_404_NOT_FOUND)


class ProgressReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        progress = LearningProgress.objects.filter(user=user).first()
        sessions = LearningSession.objects.filter(user=user)
        total_sessions = sessions.count()
        total_time = sessions.aggregate(Sum('duration'))['duration__sum'] or 0

        report = {
            'quizzes_taken': progress.total_quizzes_taken if progress else 0,
            'quizzes_passed': progress.total_quizzes_passed if progress else 0,
            'average_score': float(progress.average_score) if progress else 0.0,
            'total_time_spent': total_time,
            'current_streak': progress.current_streak if progress else 0,
            'longest_streak': progress.longest_streak if progress else 0,
            'total_sessions': total_sessions
        }
        return Response(report, status=status.HTTP_200_OK)


class DailyGoalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        goal, _ = DailyGoal.objects.get_or_create(user=user, date=today)
        serializer = DailyGoalSerializer(goal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        today = timezone.now().date()
        goal, created = DailyGoal.objects.get_or_create(user=user, date=today)
        serializer = DailyGoalSerializer(goal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LearningSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        sessions = LearningSession.objects.filter(user=user).order_by('-start_time')
        serializer = LearningSessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        session = LearningSession.objects.create(user=request.user)
        serializer = LearningSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, session_id):
        try:
            session = LearningSession.objects.get(id=session_id, user=request.user)
            end_time = timezone.now()
            duration = (end_time - session.start_time).seconds // 60
            session.end_time = end_time
            session.duration = duration
            session.save()
            serializer = LearningSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except LearningSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


class StreakView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            progress = LearningProgress.objects.get(user=request.user)
            return Response({
                'current_streak': progress.current_streak,
                'longest_streak': progress.longest_streak
            }, status=status.HTTP_200_OK)
        except LearningProgress.DoesNotExist:
            return Response({'error': 'Progress not found'}, status=status.HTTP_404_NOT_FOUND)


class ProgressComparisonView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        progress = LearningProgress.objects.filter(user=user).first()
        if not progress:
            return Response({'message': 'No progress data available.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'quizzes_taken': progress.total_quizzes_taken,
            'quizzes_passed': progress.total_quizzes_passed,
            'average_score': float(progress.average_score),
            'total_time_spent': progress.total_time_spent,
        }, status=status.HTTP_200_OK)


class StudyAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        sessions = LearningSession.objects.filter(user=user)
        total_sessions = sessions.count()
        total_time = sessions.aggregate(Sum('duration'))['duration__sum'] or 0
        avg_duration = total_time / total_sessions if total_sessions > 0 else 0

        return Response({
            'total_sessions': total_sessions,
            'total_time_spent': total_time,
            'average_session_duration': round(avg_duration, 2)
        }, status=status.HTTP_200_OK)
