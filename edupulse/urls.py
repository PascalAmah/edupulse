"""
URL configuration for EduPulse project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger Schema View
schema_view = get_schema_view(
    openapi.Info(
        title="EduPulse API",
        default_version='v1',
        description="API documentation for EduPulse microlearning platform",
        terms_of_service="https://www.edupulse.com/terms/",
        contact=openapi.Contact(email="contact@edupulse.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Routes
    path('api/v1/', include([
        # Core module (Dev 1) - Auth & User Management
        path('auth/', include('core.urls.auth_urls')),
        path('admin/', include('core.urls.admin_urls')),
        
        # Quizzes module (Dev 2) - Quiz Logic
        path('quizzes/', include('quizzes.urls')),
        
        # Tracking module (Dev 3) - Mood, Progress, Gamification
        path('tracking/', include('tracking.urls')),
        
        # Sync module (Dev 3) - Offline Sync
        path('sync/', include('sync.urls')),
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 