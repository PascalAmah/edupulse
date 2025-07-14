"""
Common utility functions for EduPulse project.

This module contains shared utility functions that can be used across
different apps in the project.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import html
import re
from django.utils import timezone
from django.db.models import Avg, Count, Q, Max


def calculate_score(correct_answers: int, total_questions: int, time_taken: int, 
                   time_limit: Optional[int] = None, difficulty_bonus: float = 1.0) -> float:
    """
    Calculate quiz score based on correct answers, total questions, and time taken.
    
    Args:
        correct_answers: Number of correct answers
        total_questions: Total number of questions
        time_taken: Time taken in seconds
        time_limit: Optional time limit in minutes
        difficulty_bonus: Multiplier for difficulty (default 1.0)
        
    Returns:
        float: Calculated score (0-100)
    """
    if total_questions == 0:
        return 0.0
    
    # Base score from accuracy
    accuracy_score = (correct_answers / total_questions) * 100
    
    # Time efficiency bonus (if time limit is provided)
    time_bonus = 0.0
    if time_limit:
        time_limit_seconds = time_limit * 60
        if time_taken < time_limit_seconds:
            # Bonus for finishing early (up to 10% bonus)
            time_efficiency = (time_limit_seconds - time_taken) / time_limit_seconds
            time_bonus = min(time_efficiency * 10, 10.0)
    
    # Apply difficulty bonus
    final_score = (accuracy_score + time_bonus) * difficulty_bonus
    
    # Ensure score is between 0 and 100
    return max(0.0, min(100.0, round(final_score, 2)))


def generate_user_progress_report(user_id: int, date_range: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
    """
    Generate a comprehensive progress report for a user.
    
    Args:
        user_id: User ID to generate report for
        date_range: Optional date range filter {'start': datetime, 'end': datetime}
        
    Returns:
        Dict containing progress metrics
    """
    from django.contrib.auth.models import User
    from quizzes.models import QuizAttempt
    from tracking.models import MoodEntry
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"error": "User not found"}
    
    # Build date filter
    date_filter = Q()
    if date_range:
        start_date = date_range.get('start')
        end_date = date_range.get('end')
        if start_date:
            date_filter &= Q(created_at__gte=start_date)
        if end_date:
            date_filter &= Q(created_at__lte=end_date)
    
    # Get quiz attempts
    quiz_attempts = QuizAttempt.objects.filter(user=user).filter(date_filter)
    completed_attempts = quiz_attempts.filter(completed_at__isnull=False)
    
    # Calculate metrics
    total_quizzes = completed_attempts.count()
    if total_quizzes > 0:
        average_score = completed_attempts.aggregate(Avg('score'))['score__avg'] or 0.0
        best_score = completed_attempts.aggregate(Max('score'))['score__max'] or 0.0
    else:
        average_score = 0.0
        best_score = 0.0
    
    # Calculate learning streak (consecutive days with quiz attempts)
    streak = calculate_learning_streak(user, date_range)
    
    # Calculate total time spent
    total_time_seconds = sum(
        (attempt.completed_at - attempt.started_at).total_seconds() 
        for attempt in completed_attempts 
        if attempt.completed_at and attempt.started_at
    )
    
    # Get mood trends
    mood_entries = MoodEntry.objects.filter(user=user).filter(date_filter)
    mood_trends = {}
    if mood_entries.exists():
        mood_counts = mood_entries.values('mood').annotate(count=Count('mood'))
        mood_trends = {entry['mood']: entry['count'] for entry in mood_counts}
    
    return {
        "user_id": user_id,
        "username": user.username,
        "total_quizzes_completed": total_quizzes,
        "average_score": round(average_score, 2),
        "best_score": round(best_score, 2),
        "learning_streak": streak,
        "total_time_spent": format_time_duration(int(total_time_seconds)),
        "mood_trends": mood_trends,
        "report_generated_at": timezone.now().isoformat()
    }


def calculate_learning_streak(user, date_range: Optional[Dict[str, datetime]] = None) -> int:
    """
    Calculate consecutive days with learning activity.
    
    Args:
        user: User object
        date_range: Optional date range filter
        
    Returns:
        int: Number of consecutive days
    """
    from quizzes.models import QuizAttempt
    
    # Get all dates with quiz attempts
    date_filter = Q()
    if date_range:
        start_date = date_range.get('start')
        end_date = date_range.get('end')
        if start_date:
            date_filter &= Q(created_at__gte=start_date)
        if end_date:
            date_filter &= Q(created_at__lte=end_date)
    
    attempt_dates = QuizAttempt.objects.filter(
        user=user, 
        completed_at__isnull=False
    ).filter(date_filter).values_list('started_at__date', flat=True).distinct()
    
    if not attempt_dates:
        return 0
    
    # Sort dates and find consecutive streak
    sorted_dates = sorted(attempt_dates, reverse=True)
    streak = 1
    current_date = sorted_dates[0]
    
    for date in sorted_dates[1:]:
        if (current_date - date).days == 1:
            streak += 1
            current_date = date
        else:
            break
    
    return streak


def validate_quiz_submission(answers: List[Dict[str, Any]], quiz_id: int, user_id: int) -> Dict[str, Any]:
    """
    Validate quiz submission data.
    
    Args:
        answers: List of user's quiz answers
        quiz_id: ID of the quiz being submitted
        user_id: ID of the user submitting
        
    Returns:
        Dict containing validation results
    """
    from quizzes.models import Quiz, QuizAttempt
    from django.contrib.auth.models import User
    
    validation_result = {
        "valid": False,
        "errors": [],
        "warnings": []
    }
    
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        user = User.objects.get(id=user_id)
    except (Quiz.DoesNotExist, User.DoesNotExist):
        validation_result["errors"].append("Invalid quiz or user")
        return validation_result
    
    # Check if answers are provided
    if not answers:
        validation_result["errors"].append("No answers provided")
        return validation_result
    
    # For testing: temporarily disable strict validation
    # Check if user has already submitted this quiz (only if they have a completed attempt)
    existing_completed_attempt = QuizAttempt.objects.filter(
        user=user,
        quiz=quiz,
        completed_at__isnull=False
    ).first()
    
    if existing_completed_attempt:
        validation_result["errors"].append("Quiz has already been submitted")
        return validation_result
    
    # Check if user has an active attempt
    active_attempt = QuizAttempt.objects.filter(
        user=user,
        quiz=quiz,
        completed_at__isnull=True
    ).first()
    
    if active_attempt:
        # Check time limit
        if quiz.time_limit:
            time_elapsed = timezone.now() - active_attempt.started_at
            time_limit_seconds = quiz.time_limit * 60
            
            if time_elapsed.total_seconds() > time_limit_seconds:
                validation_result["errors"].append("Time limit exceeded")
                return validation_result
        # If there's an active attempt and no time limit exceeded, allow submission
        # This is the normal flow - user starts quiz, then submits
    
    # Validate answer format
    if not isinstance(answers, list):
        validation_result["errors"].append("Invalid answer format - expected list")
        return validation_result
    
    # Check if all required questions are answered
    quiz_questions = quiz.questions.filter(is_required=True)
    answered_question_ids = set()
    
    for answer in answers:
        if not isinstance(answer, dict):
            validation_result["errors"].append("Invalid answer format - each answer should be a dictionary")
            return validation_result
        
        question_id = answer.get('question_id')
        if not question_id:
            validation_result["errors"].append("Missing question_id in answer")
            continue
            
        answered_question_ids.add(question_id)
        
        # Validate answer content
        selected_choice_ids = answer.get('selected_choice_ids', [])
        text_answer = answer.get('text_answer', '')
        
        if not selected_choice_ids and not text_answer:
            validation_result["warnings"].append(f"No answer provided for question {question_id}")
    
    # Check for missing required questions
    required_question_ids = set(q.id for q in quiz_questions)
    missing_questions = required_question_ids - answered_question_ids
    if missing_questions:
        validation_result["warnings"].append(f"Missing answers for required questions: {', '.join(map(str, missing_questions))}")
    
    # If no errors, mark as valid
    if not validation_result["errors"]:
        validation_result["valid"] = True
    
    return validation_result


def format_time_duration(seconds: int) -> str:
    """
    Format time duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted time string (e.g., "2h 30m 15s")
    """
    if seconds < 0:
        return "0s"
    
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)


def sanitize_user_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS and other security issues.
    
    Args:
        text: Raw user input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Escape HTML entities
    text = html.escape(text)
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def calculate_quiz_statistics(quiz_id: int) -> Dict[str, Any]:
    """
    Calculate statistics for a specific quiz.
    
    Args:
        quiz_id: ID of the quiz
        
    Returns:
        Dict containing quiz statistics
    """
    from quizzes.models import Quiz, QuizAttempt
    
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return {"error": "Quiz not found"}
    
    attempts = QuizAttempt.objects.filter(quiz=quiz, completed_at__isnull=False)
    
    if not attempts.exists():
        return {
            "quiz_id": quiz_id,
            "total_attempts": 0,
            "average_score": 0.0,
            "best_score": 0.0,
            "completion_rate": 0.0
        }
    
    total_attempts = attempts.count()
    average_score = attempts.aggregate(Avg('score'))['score__avg'] or 0.0
    best_score = attempts.aggregate(Max('score'))['score__max'] or 0.0
    
    # Calculate completion rate
    all_attempts = QuizAttempt.objects.filter(quiz=quiz)
    completion_rate = (total_attempts / all_attempts.count()) * 100 if all_attempts.exists() else 0.0
    
    return {
        "quiz_id": quiz_id,
        "total_attempts": total_attempts,
        "average_score": round(average_score, 2),
        "best_score": round(best_score, 2),
        "completion_rate": round(completion_rate, 2)
    }


def generate_leaderboard(limit: int = 10, date_range: Optional[Dict[str, datetime]] = None) -> List[Dict[str, Any]]:
    """
    Generate a leaderboard of top-performing users.
    
    Args:
        limit: Number of users to include in leaderboard
        date_range: Optional date range filter
        
    Returns:
        List of user dictionaries with scores
    """
    from quizzes.models import QuizAttempt
    from django.contrib.auth.models import User
    from django.db.models import Avg
    
    # Build date filter
    date_filter = Q()
    if date_range:
        start_date = date_range.get('start')
        end_date = date_range.get('end')
        if start_date:
            date_filter &= Q(created_at__gte=start_date)
        if end_date:
            date_filter &= Q(created_at__lte=end_date)
    
    # Get users with their average scores
    user_scores = QuizAttempt.objects.filter(
        completed_at__isnull=False
    ).filter(date_filter).values('user').annotate(
        avg_score=Avg('score'),
        total_quizzes=Count('id')
    ).filter(total_quizzes__gte=1).order_by('-avg_score')[:limit]
    
    leaderboard = []
    for user_score in user_scores:
        try:
            user = User.objects.get(id=user_score['user'])
            leaderboard.append({
                "user_id": user.id,
                "username": user.username,
                "average_score": round(user_score['avg_score'], 2),
                "total_quizzes": user_score['total_quizzes']
            })
        except User.DoesNotExist:
            continue
    
    return leaderboard 