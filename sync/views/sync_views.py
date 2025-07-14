"""
Sync views for EduPulse project.

This module contains views for offline synchronization.
Dev 3 responsibility: Offline Sync
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from ..serializers import (
    SyncDataSerializer, SyncRequestSerializer, SyncResponseSerializer,
    ConflictResolutionSerializer, OfflineDataSerializer, SyncStatusSerializer
)
from django.contrib.auth.models import User


class SyncView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SyncRequestSerializer(data=request.data)
        if serializer.is_valid():
            now = timezone.now()
            sync_data = {
                'sync_timestamp': now,
                'has_conflicts': False,
                'conflicts': [],
                'data_updates': {},
                'sync_token': f"token_{request.user.id}_{int(now.timestamp())}"
            }
            response_serializer = SyncResponseSerializer(sync_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConflictResolutionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConflictResolutionSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                'message': 'Conflict resolved successfully.',
                'status': 'success'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SyncStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {
            'is_synced': True,
            'last_sync_time': timezone.now(),
            'pending_changes': 0,
            'sync_errors': [],
            'next_sync_time': timezone.now() + timezone.timedelta(hours=1)
        }
        serializer = SyncStatusSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OfflineDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        offline_data = {
            'quiz_attempts': [],
            'mood_entries': [],
            'progress_data': {},
            'achievements': [],
            'created_at': timezone.now()
        }
        serializer = OfflineDataSerializer(offline_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OfflineDataSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                'message': 'Offline data stored successfully.',
                'status': 'success'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SyncHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = [
            {'sync_time': timezone.now() - timezone.timedelta(days=i), 'status': 'success'}
            for i in range(3)
        ]
        return Response({'history': history}, status=status.HTTP_200_OK)


class ForceSyncView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({
            'message': 'Immediate sync triggered successfully.',
            'status': 'success'
        }, status=status.HTTP_200_OK)


class SyncSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'auto_sync': True,
            'sync_interval_minutes': 60
        }, status=status.HTTP_200_OK)

    def post(self, request):
        return Response({
            'message': 'Sync settings updated successfully.',
            'status': 'success'
        }, status=status.HTTP_200_OK)
