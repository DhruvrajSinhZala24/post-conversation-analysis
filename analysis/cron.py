"""
Cron job to automatically analyze new conversations.
This runs daily at 12 AM (configured in settings.py).
"""
from django.utils import timezone
from datetime import timedelta
from .models import Conversation, ConversationAnalysis
from .analyzer import ConversationAnalyzer


def analyze_new_conversations():
    """
    Analyze all conversations that haven't been analyzed yet.
    This function is called by the cron job.
    """
    analyzer = ConversationAnalyzer()
    
    # Get all unanalyzed conversations
    unanalyzed_conversations = Conversation.objects.filter(analyzed=False)
    
    analyzed_count = 0
    
    for conversation in unanalyzed_conversations:
        # Get messages
        messages = [
            {'sender': msg.sender, 'message': msg.text}
            for msg in conversation.messages.all()
        ]
        
        if not messages:
            continue
        
        # Perform analysis
        analysis_data = analyzer.analyze(messages)
        
        # Create or update analysis
        ConversationAnalysis.objects.update_or_create(
            conversation=conversation,
            defaults=analysis_data
        )
        
        # Mark as analyzed
        conversation.analyzed = True
        conversation.save()
        
        analyzed_count += 1
    
    print(f"Cron job completed: Analyzed {analyzed_count} new conversations.")
    return f"Analyzed {analyzed_count} new conversations."

