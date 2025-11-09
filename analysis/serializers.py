from rest_framework import serializers
from .models import Conversation, Message, ConversationAnalysis


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'timestamp']


class ConversationAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationAnalysis
        fields = [
            'id', 'clarity_score', 'relevance_score', 'accuracy_score',
            'completeness_score', 'sentiment', 'empathy_score',
            'response_time_avg', 'resolution', 'escalation_need',
            'fallback_frequency', 'overall_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    analysis = ConversationAnalysisSerializer(read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'analyzed', 'messages', 'analysis']
        read_only_fields = ['id', 'created_at', 'analyzed']


class ConversationCreateSerializer(serializers.Serializer):
    """Serializer for creating conversations from JSON input."""
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    messages = serializers.ListField(
        child=serializers.DictField(),
        required=True
    )
    
    def validate_messages(self, value):
        """Validate message format."""
        for msg in value:
            if 'sender' not in msg or 'message' not in msg:
                raise serializers.ValidationError(
                    "Each message must have 'sender' and 'message' fields."
                )
            if msg['sender'].lower() not in ['user', 'ai']:
                raise serializers.ValidationError(
                    "Sender must be 'user' or 'ai'."
                )
        return value
    
    def create(self, validated_data):
        """Create conversation and messages from validated data."""
        conversation = Conversation.objects.create(
            title=validated_data.get('title', '')
        )
        
        for msg_data in validated_data['messages']:
            Message.objects.create(
                conversation=conversation,
                sender=msg_data['sender'].lower(),
                text=msg_data['message']
            )
        
        return conversation

