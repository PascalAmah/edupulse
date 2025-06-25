"""
Tracking models for EduPulse project.

This module contains models for mood tracking, progress monitoring, and gamification.
Dev 3 responsibility: Mood, Progress, Gamification
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class MoodEntry(models.Model):
    """
    Model for tracking user mood entries.
    """
    MOOD_CHOICES = [
        (1, 'Very Sad'),
        (2, 'Sad'),
        (3, 'Neutral'),
        (4, 'Happy'),
        (5, 'Very Happy'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_entries')
    mood_level = models.IntegerField(choices=MOOD_CHOICES)
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mood_entries'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - Mood {self.mood_level} at {self.timestamp}"


class LearningProgress(models.Model):
    """
    Model for tracking user learning progress.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_progress')
    total_quizzes_taken = models.IntegerField(default=0)
    total_quizzes_passed = models.IntegerField(default=0)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_time_spent = models.IntegerField(default=0, help_text='Total time spent learning in minutes')
    current_streak = models.IntegerField(default=0, help_text='Current learning streak in days')
    longest_streak = models.IntegerField(default=0, help_text='Longest learning streak in days')
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_progress'
        verbose_name_plural = 'Learning Progress'
    
    def __str__(self):
        return f"{self.user.username} - Progress"


class Achievement(models.Model):
    """
    Model for user achievements and badges.
    """
    ACHIEVEMENT_TYPES = [
        ('quiz_master', 'Quiz Master'),
        ('streak_king', 'Streak King'),
        ('speed_demon', 'Speed Demon'),
        ('perfect_score', 'Perfect Score'),
        ('early_bird', 'Early Bird'),
        ('night_owl', 'Night Owl'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text='Icon identifier for the achievement')
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'achievements'
        unique_together = ['user', 'achievement_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Points(models.Model):
    """
    Model for tracking user points and XP.
    """
    POINT_TYPES = [
        ('quiz_completion', 'Quiz Completion'),
        ('streak_bonus', 'Streak Bonus'),
        ('perfect_score', 'Perfect Score'),
        ('daily_login', 'Daily Login'),
        ('achievement', 'Achievement'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points')
    points_type = models.CharField(max_length=20, choices=POINT_TYPES)
    points_earned = models.IntegerField()
    description = models.CharField(max_length=200)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'points'
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.points_earned} points for {self.points_type}"


class Level(models.Model):
    """
    Model for user levels and progression.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='levels')
    current_level = models.IntegerField(default=1)
    current_xp = models.IntegerField(default=0)
    xp_to_next_level = models.IntegerField(default=100)
    total_xp_earned = models.IntegerField(default=0)
    last_level_up = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'levels'
    
    def __str__(self):
        return f"{self.user.username} - Level {self.current_level}"


class DailyGoal(models.Model):
    """
    Model for tracking daily learning goals.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_goals')
    date = models.DateField()
    quizzes_target = models.IntegerField(default=1)
    quizzes_completed = models.IntegerField(default=0)
    time_target = models.IntegerField(default=30, help_text='Target time in minutes')
    time_spent = models.IntegerField(default=0, help_text='Time spent in minutes')
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'daily_goals'
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username} - Daily Goal {self.date}"


class LearningSession(models.Model):
    """
    Model for tracking individual learning sessions.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(help_text='Duration in minutes', null=True, blank=True)
    quizzes_taken = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'learning_sessions'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username} - Session {self.start_time}" 