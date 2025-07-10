"""
Gamification views for EduPulse project.

This module contains views for gamification features.
Dev 3 responsibility: Mood, Progress, Gamification
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count
from ..models import Achievement, Points, Level, DailyGoal, LearningSession
from ..serializers import AchievementSerializer, PointsSerializer, LevelSerializer


class AchievementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        achievements = Achievement.objects.filter(user=request.user)
        serializer = AchievementSerializer(achievements, many=True)
        return Response({
            'achievements': serializer.data,
            'total': achievements.count(),
        }, status=status.HTTP_200_OK)


class PointsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        points = Points.objects.filter(user=request.user)
        total_points = points.aggregate(total=Sum('points_earned'))['total'] or 0
        serializer = PointsSerializer(points, many=True)
        return Response({
            'total_points': total_points,
            'history': serializer.data
        }, status=status.HTTP_200_OK)


class LevelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            level = Level.objects.get(user=request.user)
            serializer = LevelSerializer(level)
            xp_progress = (level.current_xp / level.xp_to_next_level) * 100 if level.xp_to_next_level else 0
            return Response({
                'level': serializer.data,
                'xp_progress_percent': round(xp_progress, 2)
            }, status=status.HTTP_200_OK)
        except Level.DoesNotExist:
            return Response({'error': 'Level not found.'}, status=status.HTTP_404_NOT_FOUND)


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        top_levels = Level.objects.all().order_by('-current_level', '-total_xp_earned')[:10]
        leaderboard = [
            {
                'username': l.user.username,
                'level': l.current_level,
                'total_xp': l.total_xp_earned
            } for l in top_levels
        ]

        try:
            user_level = Level.objects.get(user=request.user)
            user_rank = Level.objects.filter(
                total_xp_earned__gt=user_level.total_xp_earned
            ).count() + 1
        except Level.DoesNotExist:
            user_rank = None

        return Response({
            'leaderboard': leaderboard,
            'your_rank': user_rank
        }, status=status.HTTP_200_OK)


class GamificationStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        achievements = Achievement.objects.filter(user=request.user).count()
        total_points = Points.objects.filter(user=request.user).aggregate(total=Sum('points_earned'))['total'] or 0
        level = Level.objects.filter(user=request.user).first()

        return Response({
            'achievements_count': achievements,
            'total_points': total_points,
            'current_level': level.current_level if level else 1
        }, status=status.HTTP_200_OK)


class RewardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        goals = DailyGoal.objects.filter(user=request.user).order_by('-date')
        reward_eligible = goals.filter(is_completed=True).exists()
        return Response({
            'completed_goal_today': reward_eligible,
            'daily_goals': goals.count()
        }, status=status.HTTP_200_OK)

    def post(self, request, reward_id):
        return Response({
            'message': f'Claim reward endpoint for reward {reward_id} - Dev 3 to implement',
            'status': 'success'
        }, status=status.HTTP_200_OK)


class ChallengeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': 'Challenge listing - logic to be implemented later'
        }, status=status.HTTP_200_OK)

    def post(self, request, challenge_id):
        return Response({
            'message': f'Join challenge endpoint for challenge {challenge_id} - Dev 3 to implement'
        }, status=status.HTTP_200_OK)


class BadgeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        badges = Achievement.objects.filter(user=request.user)
        serializer = AchievementSerializer(badges, many=True)
        return Response({
            'badges': serializer.data,
            'count': badges.count()
        }, status=status.HTTP_200_OK)
