"""
Sync serializers for EduPulse project.

This module contains serializers for offline synchronization.
Dev 3 responsibility: Offline Sync
"""

from rest_framework import serializers
from django.contrib.auth.models import User


class SyncDataSerializer(serializers.Serializer):
    """
    Serializer for syncing data between client and server.
    """
    user_id = serializers.IntegerField()
    last_sync_timestamp = serializers.DateTimeField()
    data_type = serializers.CharField(max_length=50)
    data = serializers.JSONField()
    
    def validate_data_type(self, value):
        # TODO: Implement data type validation
        # Validate that data_type is one of the allowed types
        allowed_types = ['quiz_attempts', 'mood_entries', 'progress_data', 'achievements']
        if value not in allowed_types:
            raise serializers.ValidationError(f"Invalid data type: {value}")
        return value


class SyncRequestSerializer(serializers.Serializer):
    """
    Serializer for sync requests from client.
    """
    user_id = serializers.IntegerField()
    last_sync_timestamp = serializers.DateTimeField()
    device_id = serializers.CharField(max_length=100)
    sync_token = serializers.CharField(max_length=200, required=False)
    
    def validate(self, attrs):
        # TODO: Implement sync request validation
        # Validate user exists and sync token if provided
        return attrs


class SyncResponseSerializer(serializers.Serializer):
    """
    Serializer for sync responses to client.
    """
    sync_timestamp = serializers.DateTimeField()
    has_conflicts = serializers.BooleanField()
    conflicts = serializers.ListField(required=False)
    data_updates = serializers.JSONField()
    sync_token = serializers.CharField(max_length=200)
    
    class Meta:
        fields = [
            'sync_timestamp', 'has_conflicts', 'conflicts',
            'data_updates', 'sync_token'
        ]


class ConflictResolutionSerializer(serializers.Serializer):
    """
    Serializer for conflict resolution.
    """
    conflict_id = serializers.CharField(max_length=100)
    resolution = serializers.ChoiceField(choices=[
        ('server', 'Use Server Version'),
        ('client', 'Use Client Version'),
        ('merge', 'Merge Data')
    ])
    merged_data = serializers.JSONField(required=False)
    
    def validate(self, attrs):
        # TODO: Implement conflict resolution validation
        # Validate that merged_data is provided when resolution is 'merge'
        if attrs['resolution'] == 'merge' and 'merged_data' not in attrs:
            raise serializers.ValidationError("Merged data is required for merge resolution")
        return attrs


class OfflineDataSerializer(serializers.Serializer):
    """
    Serializer for offline data storage.
    """
    quiz_attempts = serializers.ListField(required=False)
    mood_entries = serializers.ListField(required=False)
    progress_data = serializers.DictField(required=False)
    achievements = serializers.ListField(required=False)
    created_at = serializers.DateTimeField()
    
    def validate(self, attrs):
        # TODO: Implement offline data validation
        # Validate that at least one data type is provided
        data_types = ['quiz_attempts', 'mood_entries', 'progress_data', 'achievements']
        if not any(attrs.get(data_type) for data_type in data_types):
            raise serializers.ValidationError("At least one data type must be provided")
        return attrs


class SyncStatusSerializer(serializers.Serializer):
    """
    Serializer for sync status information.
    """
    is_synced = serializers.BooleanField()
    last_sync_time = serializers.DateTimeField()
    pending_changes = serializers.IntegerField()
    sync_errors = serializers.ListField(required=False)
    next_sync_time = serializers.DateTimeField(required=False)
    
    class Meta:
        fields = [
            'is_synced', 'last_sync_time', 'pending_changes',
            'sync_errors', 'next_sync_time'
        ] 