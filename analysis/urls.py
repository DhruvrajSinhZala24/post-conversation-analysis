from django.urls import path
from . import views

# API endpoints (accessed via /api/)
api_patterns = [
    path('conversations/', views.ConversationListView.as_view(), name='api-conversation-list'),
    path('analyse/', views.AnalyzeView.as_view(), name='api-analyze'),
    path('reports/', views.ReportsView.as_view(), name='api-reports'),
    path('upload/', views.upload_file, name='api-upload-file'),
]

# Frontend endpoints (accessed via root /)
frontend_patterns = [
    path('', views.home_view, name='home'),
    path('create/', views.create_conversation_view, name='create-conversation'),
    path('conversations/', views.conversations_view, name='conversations'),
    path('conversations/<int:conversation_id>/', views.conversation_detail_view, name='conversation-detail'),
    path('conversations/<int:conversation_id>/analyze/', views.analyze_conversation_view, name='analyze-conversation'),
    path('reports/', views.reports_view, name='reports'),
]

# Default urlpatterns for backward compatibility
urlpatterns = []

