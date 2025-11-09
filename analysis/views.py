from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Conversation, ConversationAnalysis
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    ConversationAnalysisSerializer
)
from .analyzer import ConversationAnalyzer
import json


class ConversationListView(APIView):
    """Handle conversation creation and listing."""
    
    def post(self, request):
        """Create a new conversation from JSON input.
        
        Accepts either:
        1. {"title": "...", "messages": [...]}
        2. [{"sender": "...", "message": "..."}, ...] (direct array format)
        """
        data = request.data
        
        # Handle direct array format (as shown in requirement)
        if isinstance(data, list):
            data = {'messages': data, 'title': ''}
        
        serializer = ConversationCreateSerializer(data=data)
        
        if serializer.is_valid():
            conversation = serializer.save()
            return Response(
                ConversationSerializer(conversation).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """List all conversations."""
        conversations = Conversation.objects.all().order_by('-created_at')
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)


class AnalyzeView(APIView):
    """Trigger analysis on a conversation."""
    
    def post(self, request):
        """Analyze a conversation by ID."""
        conversation_id = request.data.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'conversation_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Perform analysis
        analyzer = ConversationAnalyzer()
        messages = [
            {'sender': msg.sender, 'message': msg.text}
            for msg in conversation.messages.all()
        ]
        
        analysis_data = analyzer.analyze(messages)
        
        # Create or update analysis
        analysis, created = ConversationAnalysis.objects.update_or_create(
            conversation=conversation,
            defaults=analysis_data
        )
        
        # Mark conversation as analyzed
        conversation.analyzed = True
        conversation.save()
        
        serializer = ConversationAnalysisSerializer(analysis)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportsView(APIView):
    """List all conversation analysis results."""
    
    def get(self, request):
        """Get all analysis reports."""
        analyses = ConversationAnalysis.objects.all().order_by('-created_at')
        serializer = ConversationAnalysisSerializer(analyses, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def upload_file(request):
    """Upload conversation from JSON file."""
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    
    try:
        # Read and decode the file
        file_content = file.read().decode('utf-8')
        data = json.loads(file_content)
        
        # Handle both direct message array and wrapped format
        if isinstance(data, list):
            messages = data
            title = ''
        elif isinstance(data, dict):
            messages = data.get('messages', [])
            title = data.get('title', '')
        else:
            return Response(
                {'error': 'Invalid JSON format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ConversationCreateSerializer(data={
            'title': title,
            'messages': messages
        })
        
        if serializer.is_valid():
            conversation = serializer.save()
            return Response(
                ConversationSerializer(conversation).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except json.JSONDecodeError:
        return Response(
            {'error': 'Invalid JSON file'},
            status=status.HTTP_400_BAD_REQUEST
        )


# Frontend Views
def home_view(request):
    """Home page view."""
    return render(request, 'analysis/home.html')


@require_http_methods(["GET", "POST"])
def create_conversation_view(request):
    """Create conversation view."""
    if request.method == 'POST':
        try:
            # Handle file upload
            if 'file' in request.FILES:
                file = request.FILES['file']
                file_content = file.read().decode('utf-8')
                data = json.loads(file_content)
                
                if isinstance(data, list):
                    messages_data = data
                    title = request.POST.get('title', '')
                elif isinstance(data, dict):
                    messages_data = data.get('messages', [])
                    title = data.get('title', request.POST.get('title', ''))
                else:
                    messages.error(request, 'Invalid JSON format in file.')
                    return render(request, 'analysis/create_conversation.html')
            
            # Handle JSON input
            elif 'json_data' in request.POST:
                json_data = request.POST.get('json_data', '').strip()
                if not json_data:
                    messages.error(request, 'Please provide conversation data.')
                    return render(request, 'analysis/create_conversation.html')
                
                data = json.loads(json_data)
                if isinstance(data, list):
                    messages_data = data
                    title = request.POST.get('title', '')
                elif isinstance(data, dict):
                    messages_data = data.get('messages', [])
                    title = data.get('title', request.POST.get('title', ''))
                else:
                    messages.error(request, 'Invalid JSON format.')
                    return render(request, 'analysis/create_conversation.html')
            else:
                messages.error(request, 'Please provide conversation data.')
                return render(request, 'analysis/create_conversation.html')
            
            # Create conversation
            serializer = ConversationCreateSerializer(data={
                'title': title,
                'messages': messages_data
            })
            
            if serializer.is_valid():
                conversation = serializer.save()
                
                # Automatically analyze
                analyzer = ConversationAnalyzer()
                analysis_data = analyzer.analyze(messages_data)
                
                ConversationAnalysis.objects.update_or_create(
                    conversation=conversation,
                    defaults=analysis_data
                )
                
                conversation.analyzed = True
                conversation.save()
                
                messages.success(request, f'Conversation created and analyzed successfully!')
                return redirect('conversation-detail', conversation_id=conversation.id)
            else:
                messages.error(request, f'Error: {serializer.errors}')
        
        except json.JSONDecodeError:
            messages.error(request, 'Invalid JSON format. Please check your input.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'analysis/create_conversation.html')


def conversations_view(request):
    """List all conversations."""
    conversations = Conversation.objects.all().order_by('-created_at')
    return render(request, 'analysis/conversations.html', {
        'conversations': conversations
    })


def conversation_detail_view(request, conversation_id):
    """View conversation details."""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    return render(request, 'analysis/conversation_detail.html', {
        'conversation': conversation
    })


@require_http_methods(["POST"])
def analyze_conversation_view(request, conversation_id):
    """Trigger analysis on a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    analyzer = ConversationAnalyzer()
    messages_data = [
        {'sender': msg.sender, 'message': msg.text}
        for msg in conversation.messages.all()
    ]
    
    analysis_data = analyzer.analyze(messages_data)
    
    ConversationAnalysis.objects.update_or_create(
        conversation=conversation,
        defaults=analysis_data
    )
    
    conversation.analyzed = True
    conversation.save()
    
    messages.success(request, 'Conversation analyzed successfully!')
    return redirect('conversation-detail', conversation_id=conversation.id)


def reports_view(request):
    """View all analysis reports."""
    reports = ConversationAnalysis.objects.all().order_by('-created_at')
    return render(request, 'analysis/reports.html', {
        'reports': reports
    })

