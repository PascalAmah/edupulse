"""
Test cases for tracking functionality.

This module contains tests for mood tracking, progress monitoring, and gamification.
Dev 3 responsibility: Mood, Progress, Gamification
"""

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta
from tracking.models import MoodEntry


class MoodTrackingTestCase(APITestCase):
    def setUp(self):
        # Create user and token
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)

        # Add auth token to requests
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create mood entries
        MoodEntry.objects.create(user=self.user, mood_level=3, notes="Okay mood")
        MoodEntry.objects.create(user=self.user, mood_level=4, notes="Feeling better")
        MoodEntry.objects.create(
            user=self.user,
            mood_level=2,
            notes="Feeling low",
            timestamp=timezone.now() - timedelta(days=10)
        )

    def test_mood_entry_creation(self):
        url = '/api/v1/tracking/mood/'  # ✅ correct path
        data = {'mood_level': 5, 'notes': 'Excellent!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MoodEntry.objects.count(), 4)
        self.assertEqual(response.data['message'], 'Mood entry created successfully')

    def test_mood_analytics(self):
        url = '/api/v1/tracking/mood/analytics/'  # ✅ correct path
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('average_mood', response.data)
        self.assertIn('mood_distribution', response.data)

    def test_mood_history(self):
        url = '/api/v1/tracking/mood/history/30/'  # ✅ correct path
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('daily_averages', response.data)
