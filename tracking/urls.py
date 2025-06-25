"""
Tracking URL configuration for EduPulse project.

This module contains URL patterns for tracking functionality.
Dev 3 responsibility: Mood, Progress, Gamification
"""

from django.urls import path
from .views.mood_views import (
    MoodEntryView, MoodAnalyticsView, MoodHistoryView,
    MoodInsightsView, MoodReminderView
)
from .views.progress_views import (
    ProgressOverviewView, ProgressReportView, DailyGoalView,
    LearningSessionView, StreakView, ProgressComparisonView, StudyAnalyticsView
)
from .views.gamification_views import (
    AchievementView, PointsView, LevelView, LeaderboardView,
    GamificationStatsView, RewardView, ChallengeView, BadgeView
)

urlpatterns = [
    # Mood tracking endpoints
    path('mood/', MoodEntryView.as_view(), name='mood_entry'),
    path('mood/analytics/', MoodAnalyticsView.as_view(), name='mood_analytics'),
    path('mood/history/<int:days>/', MoodHistoryView.as_view(), name='mood_history'),
    path('mood/insights/', MoodInsightsView.as_view(), name='mood_insights'),
    path('mood/reminders/', MoodReminderView.as_view(), name='mood_reminders'),
    
    # Progress tracking endpoints
    path('progress/', ProgressOverviewView.as_view(), name='progress_overview'),
    path('progress/report/', ProgressReportView.as_view(), name='progress_report'),
    path('progress/goals/', DailyGoalView.as_view(), name='daily_goals'),
    path('progress/sessions/', LearningSessionView.as_view(), name='learning_sessions'),
    path('progress/sessions/<int:session_id>/', LearningSessionView.as_view(), name='end_session'),
    path('progress/streak/', StreakView.as_view(), name='learning_streak'),
    path('progress/comparison/', ProgressComparisonView.as_view(), name='progress_comparison'),
    path('progress/analytics/', StudyAnalyticsView.as_view(), name='study_analytics'),
    
    # Gamification endpoints
    path('achievements/', AchievementView.as_view(), name='achievements'),
    path('points/', PointsView.as_view(), name='points'),
    path('level/', LevelView.as_view(), name='level'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('stats/', GamificationStatsView.as_view(), name='gamification_stats'),
    path('rewards/', RewardView.as_view(), name='rewards'),
    path('rewards/<int:reward_id>/', RewardView.as_view(), name='claim_reward'),
    path('challenges/', ChallengeView.as_view(), name='challenges'),
    path('challenges/<int:challenge_id>/', ChallengeView.as_view(), name='join_challenge'),
    path('badges/', BadgeView.as_view(), name='badges'),
] 