"""
Test cases for quiz functionality.

This module contains tests for quiz logic and management.
Dev 2 responsibility: Quiz Logic
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import json

from quizzes.models import Quiz, Question, Choice, Category, QuizAttempt, QuizResponse
from core.models import UserProfile


class QuizTestCase(APITestCase):
    """
    Test cases for quiz endpoints.
    """
    
    def setUp(self):
        """
        Set up test data.
        """
        # Create test users with different roles
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role='admin'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='testpass123'
        )
        self.teacher_profile = UserProfile.objects.create(
            user=self.teacher_user,
            role='teacher'
        )
        
        self.student_user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123'
        )
        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
            role='student'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        # Create test quiz
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test quiz description',
            difficulty='medium',
            time_limit=30,
            passing_score=70,
            is_active=True,
            created_by=self.teacher_user
        )
        self.quiz.categories.add(self.category)
        
        # Create test questions
        self.question1 = Question.objects.create(
            quiz=self.quiz,
            question_text='What is 2 + 2?',
            question_type='multiple_choice',
            points=1,
            order=1,
            is_required=True,
            explanation='Basic arithmetic'
        )
        
        self.question2 = Question.objects.create(
            quiz=self.quiz,
            question_text='Is the sky blue?',
            question_type='true_false',
            points=1,
            order=2,
            is_required=True,
            explanation='Common knowledge'
        )
        
        # Create choices for question 1
        self.choice1_correct = Choice.objects.create(
            question=self.question1,
            choice_text='4',
            is_correct=True,
            order=1
        )
        self.choice1_wrong = Choice.objects.create(
            question=self.question1,
            choice_text='3',
            is_correct=False,
            order=2
        )
        
        # Create choices for question 2
        self.choice2_correct = Choice.objects.create(
            question=self.question2,
            choice_text='True',
            is_correct=True,
            order=1
        )
        self.choice2_wrong = Choice.objects.create(
            question=self.question2,
            choice_text='False',
            is_correct=False,
            order=2
        )
    
    def test_quiz_list_authenticated(self):
        """
        Test quiz listing endpoint for authenticated users.
        """
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/v1/quizzes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data[0])
        self.assertIn('title', response.data[0])
        self.assertIn('difficulty', response.data[0])
        self.assertIn('total_attempts', response.data[0])
        self.assertIn('average_score', response.data[0])
    
    def test_quiz_list_filtering(self):
        """
        Test quiz listing with filtering.
        """
        self.client.force_authenticate(user=self.student_user)
        
        # Test filtering by difficulty
        response = self.client.get('/api/v1/quizzes/?difficulty=medium')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test filtering by category
        response = self.client.get('/api/v1/quizzes/?category=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_quiz_detail_access(self):
        """
        Test quiz detail endpoint with proper access control.
        """
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f'/api/v1/quizzes/{self.quiz.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Quiz')
        self.assertIn('questions', response.data)
        self.assertIn('total_attempts', response.data)
    
    def test_quiz_detail_no_access(self):
        """
        Test quiz detail endpoint without proper access.
        """
        # Create an inactive quiz
        inactive_quiz = Quiz.objects.create(
            title='Inactive Quiz',
            is_active=False,
            created_by=self.teacher_user
        )
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f'/api/v1/quizzes/{inactive_quiz.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_start_quiz(self):
        """
        Test quiz start functionality.
        """
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(f'/api/v1/quizzes/{self.quiz.id}/start/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('attempt_id', response.data)
        self.assertIn('started_at', response.data)
        
        # Verify attempt was created
        attempt = QuizAttempt.objects.get(id=response.data['attempt_id'])
        self.assertEqual(attempt.user, self.student_user)
        self.assertEqual(attempt.quiz, self.quiz)
        self.assertIsNone(attempt.completed_at)
    
    def test_start_quiz_existing_attempt(self):
        """
        Test starting quiz when user already has an active attempt.
        """
        # Create an existing active attempt
        existing_attempt = QuizAttempt.objects.create(
            user=self.student_user,
            quiz=self.quiz,
            started_at=timezone.now()
        )
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(f'/api/v1/quizzes/{self.quiz.id}/start/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['attempt_id'], existing_attempt.id)
    
    def test_quiz_questions(self):
        """
        Test quiz questions endpoint.
        """
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f'/api/v1/quizzes/{self.quiz.id}/questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn('choices', response.data[0])
    
    def test_quiz_progress(self):
        """
        Test quiz progress endpoint.
        """
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f'/api/v1/quizzes/{self.quiz.id}/progress/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress'], 0)
        self.assertFalse(response.data['completed'])
    
    def test_quiz_progress_with_attempt(self):
        """
        Test quiz progress with existing attempt.
        """
        # Create a completed attempt
        attempt = QuizAttempt.objects.create(
            user=self.student_user,
            quiz=self.quiz,
            started_at=timezone.now() - timedelta(minutes=10),
            completed_at=timezone.now(),
            score=85.0,
            is_passed=True
        )
        
        # Create some responses
        QuizResponse.objects.create(
            attempt=attempt,
            question=self.question1,
            is_correct=True,
            points_earned=1
        )
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f'/api/v1/quizzes/{self.quiz.id}/progress/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress'], 50.0)  # 1 out of 2 questions
        self.assertTrue(response.data['completed'])
        self.assertEqual(response.data['score'], 85.0)


class QuizSubmissionTestCase(APITestCase):
    """
    Test cases for quiz submission functionality.
    """
    
    def setUp(self):
        """
        Set up test data.
        """
        # Create test users
        self.student_user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123'
        )
        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
            role='student'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='testpass123'
        )
        self.teacher_profile = UserProfile.objects.create(
            user=self.teacher_user,
            role='teacher'
        )
        
        # Create test quiz
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test quiz description',
            difficulty='medium',
            time_limit=30,
            passing_score=70,
            is_active=True,
            created_by=self.teacher_user
        )
        
        # Create test questions
        self.question1 = Question.objects.create(
            quiz=self.quiz,
            question_text='What is 2 + 2?',
            question_type='multiple_choice',
            points=1,
            order=1,
            is_required=True
        )
        
        self.question2 = Question.objects.create(
            quiz=self.quiz,
            question_text='Is the sky blue?',
            question_type='true_false',
            points=1,
            order=2,
            is_required=True
        )
        
        # Create choices
        self.choice1_correct = Choice.objects.create(
            question=self.question1,
            choice_text='4',
            is_correct=True,
            order=1
        )
        self.choice1_wrong = Choice.objects.create(
            question=self.question1,
            choice_text='3',
            is_correct=False,
            order=2
        )
        
        self.choice2_correct = Choice.objects.create(
            question=self.question2,
            choice_text='True',
            is_correct=True,
            order=1
        )
        self.choice2_wrong = Choice.objects.create(
            question=self.question2,
            choice_text='False',
            is_correct=False,
            order=2
        )
    
    def test_submit_quiz_correct_answers(self):
        """
        Test quiz submission with correct answers.
        """
        self.client.force_authenticate(user=self.student_user)
        # Start quiz first
        self.client.post(f'/api/v1/quizzes/{self.quiz.id}/start/')
        # Submit correct answers
        answers = [
            {
                'question_id': self.question1.id,
                'selected_choice_ids': [self.choice1_correct.id]
            },
            {
                'question_id': self.question2.id,
                'selected_choice_ids': [self.choice2_correct.id]
            }
        ]
        response = self.client.post(
            f'/api/v1/quizzes/{self.quiz.id}/submit/',
            data=json.dumps({'answers': answers}),
            content_type='application/json'
        )
        if response.status_code != status.HTTP_200_OK:
            print('RESPONSE DATA:', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_passed'])

    def test_submit_quiz_partial_answers(self):
        """
        Test quiz submission with partial correct answers.
        """
        self.client.force_authenticate(user=self.student_user)
        # Start quiz first
        self.client.post(f'/api/v1/quizzes/{self.quiz.id}/start/')
        # Submit one correct, one wrong
        answers = [
            {
                'question_id': self.question1.id,
                'selected_choice_ids': [self.choice1_correct.id]
            },
            {
                'question_id': self.question2.id,
                'selected_choice_ids': [self.choice2_wrong.id]
            }
        ]
        response = self.client.post(f'/api/v1/quizzes/{self.quiz.id}/submit/', {
            'answers': answers
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_passed'])

    def test_submit_quiz_with_feedback(self):
        """
        Test quiz submission with user feedback.
        """
        self.client.force_authenticate(user=self.student_user)
        # Start quiz first
        self.client.post(f'/api/v1/quizzes/{self.quiz.id}/start/')
        # Submit with feedback
        answers = [{
            'question_id': self.question1.id,
            'selected_choice_ids': [self.choice1_correct.id]
        }]
        response = self.client.post(f'/api/v1/quizzes/{self.quiz.id}/submit/', {
            'answers': answers,
            'feedback': 'Great quiz!',
            'user_difficulty_rating': 'easy'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        attempt = QuizAttempt.objects.get(user=self.student_user, quiz=self.quiz)
        self.assertEqual(attempt.feedback, 'Great quiz!')
        self.assertEqual(attempt.user_difficulty_rating, 'easy')

    def test_submit_quiz_validation_error(self):
        """
        Test quiz submission with validation errors.
        """
        self.client.force_authenticate(user=self.student_user)
        
        # Submit without starting quiz
        answers = [
            {
                'question_id': self.question1.id,
                'selected_choice_ids': [self.choice1_correct.id]
            }
        ]
        
        response = self.client.post(f'/api/v1/quizzes/{self.quiz.id}/submit/', {
            'answers': answers
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_save_answer(self):
        """
        Test saving individual answers.
        """
        self.client.force_authenticate(user=self.student_user)
        
        # Start quiz first
        self.client.post(f'/api/v1/quizzes/{self.quiz.id}/start/')
        
        # Save answer for first question
        response = self.client.post(
            f'/api/v1/quizzes/{self.quiz.id}/questions/{self.question1.id}/answer/',
            {
                'selected_choice_ids': [self.choice1_correct.id]
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('saved_at', response.data)
    
    def test_quiz_result(self):
        """
        Test quiz result retrieval.
        """
        # Create a completed attempt
        attempt = QuizAttempt.objects.create(
            user=self.student_user,
            quiz=self.quiz,
            started_at=timezone.now() - timedelta(minutes=10),
            completed_at=timezone.now(),
            score=85.0,
            is_passed=True
        )
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f'/api/v1/quizzes/{self.quiz.id}/result/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 85.0)
        self.assertTrue(response.data['is_passed'])
        self.assertIn('time_taken', response.data)
    
    def test_quiz_feedback(self):
        """
        Test quiz feedback retrieval.
        """
        # Create a completed attempt with responses
        attempt = QuizAttempt.objects.create(
            user=self.student_user,
            quiz=self.quiz,
            started_at=timezone.now() - timedelta(minutes=10),
            completed_at=timezone.now(),
            score=85.0,
            is_passed=True
        )
        
        response1 = QuizResponse.objects.create(
            attempt=attempt,
            question=self.question1,
            is_correct=True,
            points_earned=1
        )
        response1.selected_choices.add(self.choice1_correct)
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f'/api/v1/quizzes/{self.quiz.id}/feedback/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('feedback', response.data)
        self.assertEqual(len(response.data['feedback']), 1)
        self.assertTrue(response.data['feedback'][0]['is_correct'])
    
    def test_retake_quiz(self):
        """
        Test quiz retake functionality.
        """
        # Create a completed attempt for the student
        attempt = QuizAttempt.objects.create(
            user=self.student_user,
            quiz=self.quiz,
            started_at=timezone.now() - timedelta(minutes=10),
            completed_at=timezone.now(),
            score=85.0,
            is_passed=True
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(f'/api/v1/quizzes/{self.quiz.id}/retake/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['attempt_id'], attempt.id)
        # Verify old attempt was deleted
        self.assertFalse(QuizAttempt.objects.filter(id=attempt.id).exists())
    
    def test_quiz_analytics(self):
        """
        Test quiz analytics endpoint.
        """
        # Create some attempts
        QuizAttempt.objects.create(
            user=self.student_user,
            quiz=self.quiz,
            started_at=timezone.now() - timedelta(minutes=10),
            completed_at=timezone.now(),
            score=85.0,
            is_passed=True
        )
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f'/api/v1/quizzes/{self.quiz.id}/analytics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_attempts', response.data)
        self.assertIn('average_score', response.data)
        self.assertIn('completion_rate', response.data)
        self.assertIn('user_attempt', response.data)


class QuizPermissionsTestCase(APITestCase):
    """
    Test cases for quiz permissions.
    """
    
    def setUp(self):
        """
        Set up test data.
        """
        # Create test users
        self.student_user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123'
        )
        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
            role='student'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='testpass123'
        )
        self.teacher_profile = UserProfile.objects.create(
            user=self.teacher_user,
            role='teacher'
        )
        
        # Create test quiz
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            is_active=True,
            created_by=self.teacher_user
        )
        
        # Create test questions for permissions tests
        self.question1 = Question.objects.create(
            quiz=self.quiz,
            question_text='What is 2 + 2?',
            question_type='multiple_choice',
            points=1,
            order=1,
            is_required=True
        )
        
        self.question2 = Question.objects.create(
            quiz=self.quiz,
            question_text='Is the sky blue?',
            question_type='true_false',
            points=1,
            order=2,
            is_required=True
        )
        
        # Create choices for question 1
        self.choice1_correct = Choice.objects.create(
            question=self.question1,
            choice_text='4',
            is_correct=True,
            order=1
        )
        self.choice1_wrong = Choice.objects.create(
            question=self.question1,
            choice_text='3',
            is_correct=False,
            order=2
        )
        
        # Create choices for question 2
        self.choice2_correct = Choice.objects.create(
            question=self.question2,
            choice_text='True',
            is_correct=True,
            order=1
        )
        self.choice2_wrong = Choice.objects.create(
            question=self.question2,
            choice_text='False',
            is_correct=False,
            order=2
        )
    
    def test_student_can_access_quiz(self):
        """
        Test that students can access quizzes.
        """
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f'/api/v1/quizzes/{self.quiz.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_teacher_can_access_quiz(self):
        """
        Test that teachers can access quizzes.
        """
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(f'/api/v1/quizzes/{self.quiz.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthenticated_cannot_access_quiz(self):
        """
        Test that unauthenticated users cannot access quizzes.
        """
        response = self.client.get(f'/api/v1/quizzes/{self.quiz.id}/')
        # DRF returns 403 Forbidden for unauthenticated by default
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_student_can_submit_quiz(self):
        """
        Test that students can submit quizzes.
        """
        self.client.force_authenticate(user=self.student_user)
        # Start quiz first
        self.client.post(f'/api/v1/quizzes/{self.quiz.id}/start/')
        # Submit a valid answer (not empty)
        answers = [{
            'question_id': self.question1.id,
            'selected_choice_ids': [self.choice1_correct.id]
        }]
        response = self.client.post(f'/api/v1/quizzes/{self.quiz.id}/submit/', {
            'answers': answers
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_submit_quiz(self):
        """
        Test that teachers cannot submit quizzes (unless they have student role).
        """
        self.client.force_authenticate(user=self.teacher_user)
        # Start quiz first (should be forbidden for teacher)
        self.client.post(f'/api/v1/quizzes/{self.quiz.id}/start/')
        answers = [{
            'question_id': self.question1.id,
            'selected_choice_ids': [self.choice1_correct.id]
        }]
        response = self.client.post(f'/api/v1/quizzes/{self.quiz.id}/submit/', {
            'answers': answers
        })
        # Teachers should get 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 