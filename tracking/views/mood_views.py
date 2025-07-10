"""
Mood tracking views for EduPulse project.

This module contains views for mood tracking functionality.
Dev 3 responsibility: Mood, Progress, Gamification
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from ..models import MoodEntry
from ..serializers import MoodEntrySerializer, MoodTrackingSerializer


class MoodEntryView(APIView):
    """
    API view for creating and retrieving mood entries.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get user's mood entries.
        Supports optional filtering by start_date and end_date.
        """
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = MoodEntry.objects.filter(user=user)

        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)

        serializer = MoodEntrySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new mood entry.
        """
        serializer = MoodTrackingSerializer(data=request.data)
        if serializer.is_valid():
            MoodEntry.objects.create(
                user=request.user,
                mood_level=serializer.validated_data['mood_level'],
                notes=serializer.validated_data.get('notes', '')
            )
            return Response({'message': 'Mood entry created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MoodAnalyticsView(APIView):
    """
    API view for mood analytics and trends.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns average mood level and count of each mood over the past 30 days.
        """
        user = request.user
        past_30_days = timezone.now() - timedelta(days=30)
        queryset = MoodEntry.objects.filter(user=user, timestamp__gte=past_30_days)

        mood_data = {}
        mood_sum = 0

        for mood in queryset:
            mood_sum += mood.mood_level
            mood_data[mood.mood_level] = mood_data.get(mood.mood_level, 0) + 1

        total_entries = queryset.count()
        average_mood = round(mood_sum / total_entries, 2) if total_entries else 0

        return Response({
            'average_mood': average_mood,
            'mood_distribution': mood_data
        }, status=status.HTTP_200_OK)


class MoodHistoryView(APIView):
    """
    API view for getting mood history.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, days=7):
        """
        Get mood history for specified number of days.
        """
        user = request.user
        since = timezone.now() - timedelta(days=days)
        entries = MoodEntry.objects.filter(user=user, timestamp__gte=since)

        history = {}
        for entry in entries:
            day = entry.timestamp.date().isoformat()
            history.setdefault(day, []).append(entry.mood_level)

        daily_averages = {
            day: round(sum(moods) / len(moods), 2)
            for day, moods in history.items()
        }

        return Response({
            'daily_averages': daily_averages
        }, status=status.HTTP_200_OK)


class MoodInsightsView(APIView):
    """
    API view for mood insights and recommendations.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Analyze user mood patterns and give insights.
        """
        user = request.user
        recent_entries = MoodEntry.objects.filter(user=user).order_by('-timestamp')[:10]
        mood_scores = [entry.mood_level for entry in recent_entries]

        if not mood_scores:
            return Response({'insight': 'No mood data available yet.'})

        average = sum(mood_scores) / len(mood_scores)

        if average >= 4.0:
            insight = "You’ve been feeling good lately! Keep it up!"
        elif average >= 3.0:
            insight = "Your mood has been stable. Try engaging in joyful activities."
        else:
            insight = "Your mood has been low. Consider talking to a friend or taking breaks."

        return Response({
            'average_mood': round(average, 2),
            'insight': insight
        }, status=status.HTTP_200_OK)


class MoodReminderView(APIView):
    """
    API view for mood reminder settings.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Placeholder for future mood reminder logic.
        """
        return Response({
            'reminder_enabled': False,
            'message': 'Mood reminders not yet implemented'
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Placeholder for future mood reminder setting logic.
        """
        return Response({
            'message': 'Mood reminder update not yet implemented'
        }, status=status.HTTP_200_OK)
