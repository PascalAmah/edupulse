# EduPulse API Specification

## Overview

EduPulse is a microlearning platform that provides quiz-based learning with mood tracking, progress monitoring, and gamification features. This document outlines the REST API endpoints for the platform.

## Base URL

```
http://localhost:8000/api/v1/
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### Authentication (Dev 1)

#### POST /auth/register/

Register a new user.

**Request Body:**

```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "password_confirm": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "student|teacher|admin"
}
```

**Response:**

```json
{
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string"
  },
  "tokens": {
    "access": "string",
    "refresh": "string"
  }
}
```

#### POST /auth/login/

Authenticate user and get JWT tokens.

**Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**

```json
{
  "user": {
    "id": 1,
    "username": "string",
    "email": "string"
  },
  "tokens": {
    "access": "string",
    "refresh": "string"
  }
}
```

#### POST /auth/logout/

Logout user and invalidate tokens.

#### GET /auth/profile/

Get current user's profile.

#### PUT /auth/profile/

Update current user's profile.

#### POST /auth/password/reset/

Request password reset token.

#### POST /auth/password/reset/confirm/

Confirm password reset with token.

#### POST /auth/password/change/

Change user password.

#### POST /auth/refresh/

Refresh JWT access token.

### Admin Management (Dev 1)

#### GET /admin/users/

Get list of all users (admin only).

#### GET /admin/users/{user_id}/

Get specific user details (admin only).

#### PUT /admin/users/{user_id}/

Update specific user details (admin only).

#### DELETE /admin/users/{user_id}/

Deactivate specific user (admin only).

#### GET /admin/users/stats/

Get user statistics (admin only).

#### POST /admin/users/bulk-action/

Perform bulk actions on users (admin only).

#### GET /admin/sessions/

Get list of active user sessions (admin only).

#### POST /admin/sessions/{session_id}/terminate/

Terminate a specific user session (admin only).

### Quizzes (Dev 2)

#### GET /quizzes/

Get list of available quizzes.

**Query Parameters:**

- `difficulty`: easy|medium|hard
- `category`: string
- `page`: integer
- `page_size`: integer

#### GET /quizzes/{quiz_id}/

Get detailed quiz information.

#### POST /quizzes/start/

Start a new quiz attempt.

**Request Body:**

```json
{
  "quiz_id": 1
}
```

#### GET /quizzes/{quiz_id}/question/{question_number}/

Get specific question from a quiz.

#### GET /quizzes/{quiz_id}/progress/

Get user's progress on a specific quiz.

#### GET /quizzes/attempts/

Get list of user's quiz attempts.

#### POST /quizzes/submit/

Submit quiz answers.

**Request Body:**

```json
{
  "quiz_id": 1,
  "answers": [
    {
      "question_id": 1,
      "selected_choices": [1, 2],
      "text_answer": "string"
    }
  ]
}
```

#### GET /quizzes/{quiz_id}/result/

Get quiz results for a specific quiz.

#### POST /quizzes/{quiz_id}/save-answer/

Save answer for a specific question.

#### GET /quizzes/{quiz_id}/feedback/

Get detailed quiz feedback.

#### POST /quizzes/{quiz_id}/retake/

Start a new attempt for a previously taken quiz.

#### GET /quizzes/{quiz_id}/analytics/

Get analytics for a specific quiz.

### Tracking (Dev 3)

#### Mood Tracking

##### GET /tracking/mood/

Get user's mood entries.

##### POST /tracking/mood/

Create a new mood entry.

**Request Body:**

```json
{
    "mood_level": 1-5,
    "notes": "string"
}
```

##### GET /tracking/mood/analytics/

Get mood analytics and trends.

##### GET /tracking/mood/history/{days}/

Get mood history for specified number of days.

##### GET /tracking/mood/insights/

Get mood insights and recommendations.

##### GET /tracking/mood/reminders/

Get user's mood reminder settings.

##### POST /tracking/mood/reminders/

Update mood reminder settings.

#### Progress Tracking

##### GET /tracking/progress/

Get user's learning progress overview.

##### GET /tracking/progress/report/

Get detailed progress report.

##### GET /tracking/progress/goals/

Get user's daily goals.

##### POST /tracking/progress/goals/

Create or update daily goal.

##### GET /tracking/progress/sessions/

Get user's learning sessions.

##### POST /tracking/progress/sessions/

Start a new learning session.

##### PUT /tracking/progress/sessions/{session_id}/

End a learning session.

##### GET /tracking/progress/streak/

Get user's learning streak information.

##### GET /tracking/progress/comparison/

Compare progress across different time periods.

##### GET /tracking/progress/analytics/

Get detailed study analytics.

#### Gamification

##### GET /tracking/achievements/

Get user's achievements.

##### GET /tracking/points/

Get user's points and XP information.

##### GET /tracking/level/

Get user's level information.

##### GET /tracking/leaderboard/

Get leaderboard rankings.

##### GET /tracking/stats/

Get comprehensive gamification statistics.

##### GET /tracking/rewards/

Get available rewards and user's reward status.

##### POST /tracking/rewards/{reward_id}/

Claim a reward.

##### GET /tracking/challenges/

Get available challenges.

##### POST /tracking/challenges/{challenge_id}/

Join a challenge.

##### GET /tracking/badges/

Get user's badges.

### Sync (Dev 3)

#### POST /sync/

Synchronize data between client and server.

**Request Body:**

```json
{
  "user_id": 1,
  "last_sync_timestamp": "2024-01-01T00:00:00Z",
  "device_id": "string",
  "sync_token": "string"
}
```

#### POST /sync/conflicts/

Resolve sync conflicts.

#### GET /sync/status/

Get sync status for user.

#### GET /sync/offline-data/

Get offline data for user.

#### POST /sync/offline-data/

Store offline data from client.

#### GET /sync/history/

Get sync history for user.

#### POST /sync/force/

Force immediate synchronization.

#### GET /sync/settings/

Get user's sync settings.

#### POST /sync/settings/

Update user's sync settings.

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "error": "Validation error",
  "details": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized

```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden

```json
{
  "error": "Permission denied"
}
```

### 404 Not Found

```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error"
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse. Limits are applied per user and endpoint.

## Pagination

List endpoints support pagination with the following query parameters:

- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response Format:**

```json
{
    "count": 100,
    "next": "http://api.example.com/endpoint/?page=3",
    "previous": "http://api.example.com/endpoint/?page=1",
    "results": [...]
}
```

## Development Notes

- All endpoints return JSON responses
- Timestamps are in ISO 8601 format (UTC)
- IDs are integers unless otherwise specified
- Boolean values are true/false (not 1/0)
- Empty responses use null instead of empty strings/arrays
