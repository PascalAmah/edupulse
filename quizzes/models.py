"""
Quiz models for EduPulse project.

This module contains models related to quiz functionality.
Dev 2 responsibility: Quiz Logic
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Quiz(models.Model):
    """
    Model for quiz definitions.
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    time_limit = models.IntegerField(help_text='Time limit in minutes', null=True, blank=True)
    passing_score = models.IntegerField(default=70, help_text='Minimum score to pass (0-100)')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quizzes'
        verbose_name_plural = 'Quizzes'
    
    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Model for quiz questions.
    """
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    points = models.IntegerField(default=1, help_text='Points for this question')
    order = models.IntegerField(default=0, help_text='Order of question in quiz')
    is_required = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.quiz.title} - Question {self.order}"


class Choice(models.Model):
    """
    Model for question choices (for multiple choice questions).
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'choices'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question.question_text[:50]} - {self.choice_text}"


class QuizAttempt(models.Model):
    """
    Model for tracking quiz attempts by users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_passed = models.BooleanField(default=False)
    time_taken = models.IntegerField(help_text='Time taken in seconds', null=True, blank=True)
    
    class Meta:
        db_table = 'quiz_attempts'
        unique_together = ['user', 'quiz']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"


class QuizResponse(models.Model):
    """
    Model for storing user responses to quiz questions.
    """
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name='responses')
    text_answer = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'quiz_responses'
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.question_text[:50]}" 