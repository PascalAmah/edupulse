"""
Authentication views for EduPulse project.

This module contains views for user authentication and management.
Dev 1 responsibility: Auth & User Management
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, UserProfileSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer, ChangePasswordSerializer,
    LogoutSerializer, UserProfileUpdateSerializer
)
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


class RegisterView(APIView):
    """
    API view for user registration.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Register a new user account",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'tokens': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            400: openapi.Response(description="Bad request - validation errors"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def post(self, request):
        """
        Register a new user.
        """
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Create user and profile
                user = serializer.save()
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                # Return user data and tokens
                return Response({
                    'message': 'User registered successfully',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.profile.role,
                        'date_joined': user.date_joined
                    },
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'message': 'Error creating user',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'message': 'Registration failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API view for user login.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Authenticate user and return JWT tokens.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'tokens': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            400: openapi.Response(description="Invalid credentials or bad request"),
        }
    )
    def post(self, request):
        """
        Authenticate user and return JWT tokens.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.profile.role if hasattr(user, 'profile') else None,
                    'date_joined': user.date_joined
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Login failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    API view for user logout.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout user and invalidate refresh token.",
        request_body=LogoutSerializer,
        responses={
            200: openapi.Response(
                description="Logout successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description="Invalid refresh token or bad request"),
        }
    )
    def post(self, request):
        """
        Logout user and invalidate tokens.
        """
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            # token = serializer.validated_data['token']
            # try:
            #     # Attempt to blacklist the token (will only work if blacklist app is enabled)
            #     token.blacklist()
            # except AttributeError:
            #     # Blacklist app not enabled, just pass
            #     pass
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Logout failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    API view for user profile management.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get current user's profile.",
        responses={
            200: openapi.Response(
                description="User profile retrieved successfully",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            404: openapi.Response(description="Profile not found"),
        }
    )
    def get(self, request):
        """
        Get current user's profile.
        """
        user = request.user
        try:
            profile = user.profile
        except Exception:
            return Response({'message': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update current user's profile.",
        request_body=UserProfileUpdateSerializer,
        responses={
            200: openapi.Response(
                description="User profile updated successfully",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: openapi.Response(description="Invalid data"),
        }
    )
    def put(self, request):
        """
        Update current user's profile.
        """
        user = request.user
        try:
            profile = user.profile
        except Exception:
            return Response({'message': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Optionally update user fields if present
            user_data = request.data.get('user', {})
            if user_data:
                for field in ['first_name', 'last_name', 'email']:
                    if field in user_data:
                        setattr(user, field, user_data[field])
                user.save()
            return Response(UserProfileSerializer(profile).data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Update failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    API view for password reset request.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Request password reset token.
        """
        # TODO: Implement password reset request logic
        # 1. Validate email
        # 2. Generate reset token
        # 3. Send email with reset link
        return Response({
            'message': 'Password reset request endpoint - Dev 1 to implement',
            'status': 'success'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    API view for password reset confirmation.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Confirm password reset with token.
        """
        # TODO: Implement password reset confirmation logic
        # 1. Validate token
        # 2. Update password
        # 3. Invalidate token
        return Response({
            'message': 'Password reset confirmation endpoint - Dev 1 to implement',
            'status': 'success'
        }, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    API view for changing user password.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Change user password.
        """
        # TODO: Implement password change logic
        # 1. Validate old password
        # 2. Update to new password
        # 3. Invalidate existing sessions
        return Response({
            'message': 'Change password endpoint - Dev 1 to implement',
            'status': 'success'
        }, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    """
    API view for refreshing JWT tokens.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Refresh JWT access token.",
        request_body=TokenRefreshSerializer,
        responses={
            200: openapi.Response(
                description="Token refreshed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description="Invalid refresh token or bad request"),
        }
    )
    def post(self, request):
        """
        Refresh JWT access token.
        """
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Token refresh failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST) 