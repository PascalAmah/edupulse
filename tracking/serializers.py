"""
Tracking serializers for EduPulse project.

This module contains serializers for mood tracking, progress monitoring, and gamification.
Dev 3 responsibility: Mood, Progress, Gamification
"""

from rest_framework import serializers
from .models import (
    MoodEntry, LearningProgress, Achievement, Points, Level,
    DailyGoal, LearningSession
)


class MoodEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for MoodEntry model.
    """
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = MoodEntry
        fields = ['id', 'user', 'mood_level', 'notes', 'timestamp']
        read_only_fields = ['id', 'user', 'timestamp']


class LearningProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for LearningProgress model.
    """
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = LearningProgress
        fields = [
            'id', 'user', 'total_quizzes_taken', 'total_quizzes_passed',
            'average_score', 'total_time_spent', 'current_streak',
            'longest_streak', 'last_activity'
        ]
        read_only_fields = ['id', 'user', 'last_activity']


class AchievementSerializer(serializers.ModelSerializer):
    """
    Serializer for Achievement model.
    """
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Achievement
        fields = ['id', 'user', 'achievement_type', 'title', 'description', 'icon', 'earned_at']
        read_only_fields = ['id', 'user', 'earned_at']


class PointsSerializer(serializers.ModelSerializer):
    """
    Serializer for Points model.
    """
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Points
        fields = ['id', 'user', 'points_type', 'points_earned', 'description', 'earned_at']
        read_only_fields = ['id', 'user', 'earned_at']


class LevelSerializer(serializers.ModelSerializer):
    """
    Serializer for Level model.
    """
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Level
        fields = [
            'id', 'user', 'current_level', 'current_xp', 'xp_to_next_level',
            'total_xp_earned', 'last_level_up'
        ]
        read_only_fields = ['id', 'user', 'last_level_up']


class DailyGoalSerializer(serializers.ModelSerializer):
    """
    Serializer for DailyGoal model.
    """
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = DailyGoal
        fields = [
            'id', 'user', 'date', 'quizzes_target', 'quizzes_completed',
            'time_target', 'time_spent', 'is_completed'
        ]
        read_only_fields = ['id', 'user']


class LearningSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for LearningSession model.
    """
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = LearningSession
        fields = [
            'id', 'user', 'start_time', 'end_time', 'duration',
            'quizzes_taken', 'points_earned'
        ]
        read_only_fields = ['id', 'user', 'start_time']


class MoodTrackingSerializer(serializers.Serializer):
    """
    Serializer for mood tracking input.
    """
    mood_level = serializers.ChoiceField(choices=MoodEntry.MOOD_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_mood_level(self, value):
        # TODO: Implement mood level validation
        # Check if mood level is within valid range
        return value


class ProgressReportSerializer(serializers.Serializer):
    """
    Serializer for generating progress reports.
    """
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    include_mood = serializers.BooleanField(default=True)
    include_achievements = serializers.BooleanField(default=True)
    
    def validate(self, attrs):
        # TODO: Implement date range validation
        # Ensure start_date is before end_date if both provided
        return attrs


class GamificationStatsSerializer(serializers.Serializer):
    """
    Serializer for gamification statistics.
    """
    total_points = serializers.IntegerField()
    current_level = serializers.IntegerField()
    achievements_count = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    rank_percentage = serializers.FloatField(help_text='User rank as percentage')
    
    class Meta:
        fields = [
            'total_points', 'current_level', 'achievements_count',
            'current_streak', 'longest_streak', 'rank_percentage'
        ]


class LeaderboardEntrySerializer(serializers.Serializer):
    """
    Serializer for leaderboard entries.
    """
    username = serializers.CharField()
    total_points = serializers.IntegerField()
    current_level = serializers.IntegerField()
    achievements_count = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    rank = serializers.IntegerField()
    
    class Meta:
        fields = [
            'username', 'total_points', 'current_level',
            'achievements_count', 'current_streak', 'rank'
        ] 