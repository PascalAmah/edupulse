"""
Quiz serializers for EduPulse project.

This module contains serializers for quiz functionality.
Dev 2 responsibility: Quiz Logic
"""

from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizAttempt, QuizResponse


class ChoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Choice model.
    """
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'order']
        read_only_fields = ['id']


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for Question model.
    """
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'question_type', 'points', 
            'order', 'is_required', 'choices'
        ]
        read_only_fields = ['id']


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for Quiz model.
    """
    questions = QuestionSerializer(many=True, read_only=True)
    created_by = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'difficulty', 'time_limit',
            'passing_score', 'is_active', 'created_by', 'created_at',
            'updated_at', 'questions'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class QuizListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for quiz listing.
    """
    created_by = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'difficulty', 'time_limit',
            'passing_score', 'is_active', 'created_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class QuizAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer for QuizAttempt model.
    """
    user = serializers.ReadOnlyField(source='user.username')
    quiz_title = serializers.ReadOnlyField(source='quiz.title')
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'user', 'quiz', 'quiz_title', 'started_at', 'completed_at',
            'score', 'is_passed', 'time_taken'
        ]
        read_only_fields = ['id', 'user', 'started_at']


class QuizResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for QuizResponse model.
    """
    question_text = serializers.ReadOnlyField(source='question.question_text')
    selected_choice_texts = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizResponse
        fields = [
            'id', 'question', 'question_text', 'selected_choices',
            'selected_choice_texts', 'text_answer', 'is_correct',
            'points_earned', 'answered_at'
        ]
        read_only_fields = ['id', 'answered_at']
    
    def get_selected_choice_texts(self, obj):
        return [choice.choice_text for choice in obj.selected_choices.all()]


class StartQuizSerializer(serializers.Serializer):
    """
    Serializer for starting a quiz.
    """
    quiz_id = serializers.IntegerField()
    
    def validate_quiz_id(self, value):
        # TODO: Implement quiz validation logic
        # Check if quiz exists and is active
        # Check if user has access to this quiz
        return value


class SubmitQuizSerializer(serializers.Serializer):
    """
    Serializer for submitting quiz answers.
    """
    quiz_id = serializers.IntegerField()
    answers = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of answers with question_id and response data"
    )
    
    def validate(self, attrs):
        # TODO: Implement answer validation logic
        # Validate that all required questions are answered
        # Validate answer format based on question type
        return attrs


class QuizResultSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz results.
    """
    quiz_title = serializers.ReadOnlyField(source='quiz.title')
    total_questions = serializers.SerializerMethodField()
    correct_answers = serializers.SerializerMethodField()
    percentage_score = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz_title', 'score', 'is_passed', 'time_taken',
            'started_at', 'completed_at', 'total_questions',
            'correct_answers', 'percentage_score'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']
    
    def get_total_questions(self, obj):
        # TODO: Implement total questions calculation
        return 0
    
    def get_correct_answers(self, obj):
        # TODO: Implement correct answers calculation
        return 0
    
    def get_percentage_score(self, obj):
        # TODO: Implement percentage score calculation
        return 0.0 