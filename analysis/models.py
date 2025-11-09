from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    analyzed = models.BooleanField(default=False)

    def __str__(self):
        return f"Conversation {self.id} - {self.title or 'Untitled'}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.CharField(max_length=20)  # "user" or "ai"
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender}: {self.text[:50]}"


class ConversationAnalysis(models.Model):
    conversation = models.OneToOneField(
        Conversation,
        on_delete=models.CASCADE,
        related_name="analysis"
    )
    
    # Conversation Quality Parameters
    clarity_score = models.FloatField(default=0.0)
    relevance_score = models.FloatField(default=0.0)
    accuracy_score = models.FloatField(default=0.0)
    completeness_score = models.FloatField(default=0.0)
    
    # Interaction Parameters
    sentiment = models.CharField(max_length=20, default='neutral')
    empathy_score = models.FloatField(default=0.0)
    response_time_avg = models.FloatField(default=0.0)  # in seconds
    
    # Resolution Parameters
    resolution = models.BooleanField(default=False)
    escalation_need = models.BooleanField(default=False)
    
    # AI Ops Parameters
    fallback_frequency = models.IntegerField(default=0)
    
    # Overall Score
    overall_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis for Conversation {self.conversation.id}"

