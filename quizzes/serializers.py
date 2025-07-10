"""
Quiz serializers for EduPulse project.

This module contains serializers for quiz functionality.
Dev 2 updated: Quiz Logic
"""

from rest_framework import serializers
from .models import (
    Category, Quiz, Question, Choice,
    QuizAttempt, QuizResponse
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'question_text',
            'question_type',
            'points',
            'order',
            'is_required',
            'explanation',
            'choices'
        ]


class QuizSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField()
    total_questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'difficulty',
            'time_limit',
            'passing_score',
            'is_active',
            'created_by',
            'categories',
            'created_at',
            'updated_at',
            'total_questions',
            'questions'
        ]

    def get_total_questions(self, obj):
        return obj.questions.count()


class QuizResponseSerializer(serializers.ModelSerializer):
    attempt = serializers.StringRelatedField()
    question = QuestionSerializer(read_only=True)
    selected_choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = QuizResponse
        fields = [
            'id',
            'attempt',
            'question',
            'selected_choices',
            'text_answer',
            'is_correct',
            'points_earned',
            'answered_at'
        ]


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)
    user = serializers.StringRelatedField()
    correct_answers = serializers.SerializerMethodField()
    percentage_score = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = [
            'id',
            'user',
            'quiz',
            'started_at',
            'completed_at',
            'score',
            'is_passed',
            'time_taken',
            'feedback',
            'user_difficulty_rating',
            'correct_answers',
            'percentage_score'
        ]

    def get_correct_answers(self, obj):
        return obj.responses.filter(is_correct=True).count()

    def get_percentage_score(self, obj):
        total_questions = obj.quiz.questions.count()
        correct_answers = obj.responses.filter(is_correct=True).count()
        if total_questions == 0:
            return 0
        return round((correct_answers / total_questions) * 100, 2)