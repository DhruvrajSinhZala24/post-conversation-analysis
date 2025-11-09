"""
URL configuration for conversation_analysis project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """Root endpoint showing API information."""
    return JsonResponse({
        'message': 'Post-Conversation Analysis API',
        'version': '1.0',
        'endpoints': {
            'conversations': {
                'url': '/api/conversations/',
                'methods': ['GET', 'POST'],
                'description': 'List all conversations or create a new one'
            },
            'analyze': {
                'url': '/api/analyse/',
                'methods': ['POST'],
                'description': 'Trigger analysis on a conversation',
                'body': {'conversation_id': 'integer'}
            },
            'reports': {
                'url': '/api/reports/',
                'methods': ['GET'],
                'description': 'Get all conversation analysis results'
            },
            'upload': {
                'url': '/api/upload/',
                'methods': ['POST'],
                'description': 'Upload conversation from JSON file',
                'body': {'file': 'multipart/form-data'}
            },
            'admin': {
                'url': '/admin/',
                'methods': ['GET'],
                'description': 'Django admin interface'
            }
        },
        'example_request': {
            'url': '/api/conversations/',
            'method': 'POST',
            'body': {
                'title': 'Customer Support Chat',
                'messages': [
                    {'sender': 'user', 'message': 'Hi, I need help with my order.'},
                    {'sender': 'ai', 'message': 'Sure, can you please share your order ID?'}
                ]
            }
        }
    })

from analysis.urls import frontend_patterns, api_patterns

urlpatterns = [
    path('', include(frontend_patterns)),  # Frontend routes
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),  # API root documentation (must come before api_patterns)
    path('api/', include(api_patterns)),  # API routes
]

