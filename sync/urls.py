"""
Sync URL configuration for EduPulse project.

This module contains URL patterns for offline synchronization.
Dev 3 responsibility: Offline Sync
"""

from django.urls import path
from .views.sync_views import (
    SyncView, ConflictResolutionView, SyncStatusView, OfflineDataView,
    SyncHistoryView, ForceSyncView, SyncSettingsView
)

urlpatterns = [
    # Core sync endpoints
    path('', SyncView.as_view(), name='sync'),
    path('conflicts/', ConflictResolutionView.as_view(), name='conflict_resolution'),
    path('status/', SyncStatusView.as_view(), name='sync_status'),
    
    # Offline data endpoints
    path('offline-data/', OfflineDataView.as_view(), name='offline_data'),
    
    # Sync management endpoints
    path('history/', SyncHistoryView.as_view(), name='sync_history'),
    path('force/', ForceSyncView.as_view(), name='force_sync'),
    path('settings/', SyncSettingsView.as_view(), name='sync_settings'),
] 