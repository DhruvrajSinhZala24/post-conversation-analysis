"""
Post-conversation analysis module.
Analyzes chat conversations and computes various quality metrics.
"""
import re
import random
from typing import List, Dict
from datetime import datetime, timedelta


class ConversationAnalyzer:
    """Analyzes conversations and computes quality metrics."""
    
    # Keywords for sentiment analysis
    POSITIVE_KEYWORDS = [
        'thanks', 'thank you', 'great', 'excellent', 'perfect', 'awesome',
        'helpful', 'appreciate', 'good', 'nice', 'solved', 'resolved'
    ]
    
    NEGATIVE_KEYWORDS = [
        'bad', 'terrible', 'awful', 'horrible', 'frustrated', 'angry',
        'disappointed', 'unsatisfied', 'wrong', 'error', 'broken', 'issue'
    ]
    
    # Fallback phrases
    FALLBACK_PHRASES = [
        "i don't know", "i'm not sure", "i can't help", "i don't understand",
        "i'm unable to", "i cannot", "i don't have", "i'm sorry, i don't"
    ]
    
    # Empathy indicators
    EMPATHY_KEYWORDS = [
        'sorry', 'understand', 'apologize', 'feel', 'concern', 'worry',
        'help', 'support', 'assist', 'glad', 'happy to'
    ]
    
    # Resolution indicators
    RESOLUTION_KEYWORDS = [
        'resolved', 'solved', 'fixed', 'completed', 'done', 'finished',
        'taken care of', 'handled', 'sorted', 'addressed'
    ]
    
    # Escalation indicators
    ESCALATION_KEYWORDS = [
        'manager', 'supervisor', 'human', 'agent', 'representative',
        'escalate', 'transfer', 'speak to someone', 'talk to a person'
    ]

    def analyze(self, messages: List[Dict]) -> Dict:
        """
        Perform comprehensive analysis on a conversation.
        
        Args:
            messages: List of message dicts with 'sender' and 'message' keys
            
        Returns:
            Dictionary containing all analysis metrics
        """
        if not messages:
            return self._get_default_analysis()
        
        # Extract AI and user messages
        ai_messages = [msg for msg in messages if msg.get('sender', '').lower() == 'ai']
        user_messages = [msg for msg in messages if msg.get('sender', '').lower() == 'user']
        
        # Compute metrics
        analysis = {
            # Conversation Quality
            'clarity_score': self._compute_clarity(ai_messages),
            'relevance_score': self._compute_relevance(messages),
            'accuracy_score': self._compute_accuracy(ai_messages),
            'completeness_score': self._compute_completeness(ai_messages, user_messages),
            
            # Interaction
            'sentiment': self._compute_sentiment(user_messages),
            'empathy_score': self._compute_empathy(ai_messages),
            'response_time_avg': self._compute_response_time(messages),
            
            # Resolution
            'resolution': self._compute_resolution(messages),
            'escalation_need': self._compute_escalation_need(messages),
            
            # AI Ops
            'fallback_frequency': self._compute_fallback_frequency(ai_messages),
            
            # Overall Score
            'overall_score': 0.0,  # Will be computed at the end
        }
        
        # Compute overall score as weighted average
        analysis['overall_score'] = self._compute_overall_score(analysis)
        
        return analysis
    
    def _compute_clarity(self, ai_messages: List[Dict]) -> float:
        """Compute clarity score based on message length and structure."""
        if not ai_messages:
            return 0.0
        
        scores = []
        for msg in ai_messages:
            text = msg.get('message', '').lower()
            score = 0.5  # Base score
            
            # Good clarity indicators
            if 20 <= len(text) <= 200:  # Optimal length
                score += 0.2
            if any(punct in text for punct in ['.', '!', '?']):  # Proper punctuation
                score += 0.1
            if not any(word in text for word in ['um', 'uh', 'er', 'ah']):  # No filler words
                score += 0.1
            if len(text.split()) >= 5:  # Sufficient detail
                score += 0.1
            
            scores.append(min(score, 1.0))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _compute_relevance(self, messages: List[Dict]) -> float:
        """Compute relevance score based on topic consistency."""
        if len(messages) < 2:
            return 0.5
        
        # Extract keywords from first user message
        first_user_msg = next((msg for msg in messages if msg.get('sender', '').lower() == 'user'), None)
        if not first_user_msg:
            return 0.5
        
        first_keywords = set(re.findall(r'\b\w{4,}\b', first_user_msg.get('message', '').lower()))
        
        # Check if subsequent messages maintain relevance
        relevant_count = 0
        total_count = 0
        
        for msg in messages[1:]:
            text = msg.get('message', '').lower()
            msg_keywords = set(re.findall(r'\b\w{4,}\b', text))
            
            if msg_keywords:
                overlap = len(first_keywords & msg_keywords) / max(len(msg_keywords), 1)
                relevant_count += overlap
                total_count += 1
        
        return relevant_count / total_count if total_count > 0 else 0.5
    
    def _compute_accuracy(self, ai_messages: List[Dict]) -> float:
        """Compute accuracy score (simulated - would use fact-checking in production)."""
        if not ai_messages:
            return 0.0
        
        scores = []
        for msg in ai_messages:
            text = msg.get('message', '').lower()
            score = 0.7  # Base score
            
            # Negative indicators
            if any(word in text for word in ['maybe', 'probably', 'might', 'possibly']):
                score -= 0.1
            if 'i think' in text or 'i believe' in text:
                score -= 0.1
            if any(word in text for word in ['definitely', 'certainly', 'absolutely']):
                score += 0.1
            
            scores.append(max(0.0, min(1.0, score)))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _compute_completeness(self, ai_messages: List[Dict], user_messages: List[Dict]) -> float:
        """Compute completeness score based on whether questions are fully answered."""
        if not user_messages or not ai_messages:
            return 0.5
        
        # Check if user messages contain questions
        questions = []
        for msg in user_messages:
            text = msg.get('message', '')
            if '?' in text or any(word in text.lower() for word in ['how', 'what', 'when', 'where', 'why', 'can you', 'please']):
                questions.append(msg)
        
        if not questions:
            return 0.7  # No questions to answer
        
        # Check if AI responses are substantial
        completeness_scores = []
        for question in questions:
            # Simple heuristic: check if AI messages are substantial
            for ai_msg in ai_messages:
                response = ai_msg.get('message', '')
                if len(response.split()) >= 5:  # Substantial response
                    score = 0.5
                    if len(response.split()) >= 10:  # More detailed
                        score += 0.3
                    if len(response) > 50:  # Detailed response
                        score += 0.2
                    completeness_scores.append(min(score, 1.0))
                    break
        
        return sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.5
    
    def _compute_sentiment(self, user_messages: List[Dict]) -> str:
        """Determine overall user sentiment."""
        if not user_messages:
            return 'neutral'
        
        positive_count = 0
        negative_count = 0
        
        for msg in user_messages:
            text = msg.get('message', '').lower()
            if any(keyword in text for keyword in self.POSITIVE_KEYWORDS):
                positive_count += 1
            if any(keyword in text for keyword in self.NEGATIVE_KEYWORDS):
                negative_count += 1
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _compute_empathy(self, ai_messages: List[Dict]) -> float:
        """Compute empathy score based on empathetic language."""
        if not ai_messages:
            return 0.0
        
        empathy_scores = []
        for msg in ai_messages:
            text = msg.get('message', '').lower()
            score = 0.3  # Base score
            
            # Check for empathy keywords
            empathy_count = sum(1 for keyword in self.EMPATHY_KEYWORDS if keyword in text)
            score += min(empathy_count * 0.15, 0.5)
            
            # Check for apologetic language
            if any(word in text for word in ['sorry', 'apologize', 'apology']):
                score += 0.2
            
            empathy_scores.append(min(score, 1.0))
        
        return sum(empathy_scores) / len(empathy_scores) if empathy_scores else 0.0
    
    def _compute_response_time(self, messages: List[Dict]) -> float:
        """Compute average response time (mock data - in production would use actual timestamps)."""
        if len(messages) < 2:
            return 0.0
        
        # Generate mock response times (in seconds)
        # In production, this would use actual timestamps from messages
        response_times = []
        for i in range(len(messages) - 1):
            # Simulate response time between 5-60 seconds
            response_times.append(random.uniform(5.0, 60.0))
        
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    def _compute_resolution(self, messages: List[Dict]) -> bool:
        """Determine if the issue was resolved."""
        # Check last few messages for resolution indicators
        last_messages = messages[-3:] if len(messages) >= 3 else messages
        combined_text = ' '.join([msg.get('message', '').lower() for msg in last_messages])
        
        if any(keyword in combined_text for keyword in self.RESOLUTION_KEYWORDS):
            return True
        
        # Check if user seems satisfied in last message
        last_user_msg = next((msg for msg in reversed(messages) if msg.get('sender', '').lower() == 'user'), None)
        if last_user_msg:
            text = last_user_msg.get('message', '').lower()
            if any(word in text for word in ['thanks', 'thank you', 'great', 'perfect', 'solved']):
                return True
        
        return False
    
    def _compute_escalation_need(self, messages: List[Dict]) -> bool:
        """Determine if conversation should be escalated."""
        combined_text = ' '.join([msg.get('message', '').lower() for msg in messages])
        
        # Check for escalation keywords
        if any(keyword in combined_text for keyword in self.ESCALATION_KEYWORDS):
            return True
        
        # Check for high negative sentiment
        user_messages = [msg for msg in messages if msg.get('sender', '').lower() == 'user']
        negative_count = sum(
            1 for msg in user_messages
            if any(keyword in msg.get('message', '').lower() for keyword in self.NEGATIVE_KEYWORDS)
        )
        
        if negative_count >= 2:  # Multiple negative messages
            return True
        
        return False
    
    def _compute_fallback_frequency(self, ai_messages: List[Dict]) -> int:
        """Count how many times AI used fallback phrases."""
        fallback_count = 0
        
        for msg in ai_messages:
            text = msg.get('message', '').lower()
            if any(phrase in text for phrase in self.FALLBACK_PHRASES):
                fallback_count += 1
        
        return fallback_count
    
    def _compute_overall_score(self, analysis: Dict) -> float:
        """Compute overall satisfaction score as weighted average."""
        weights = {
            'clarity_score': 0.15,
            'relevance_score': 0.15,
            'accuracy_score': 0.15,
            'completeness_score': 0.15,
            'empathy_score': 0.10,
            'resolution': 0.20,  # Boolean, convert to 1.0 or 0.0
            'fallback_frequency': -0.10,  # Negative weight (fewer is better)
        }
        
        score = 0.0
        total_weight = 0.0
        
        for key, weight in weights.items():
            if key == 'resolution':
                value = 1.0 if analysis[key] else 0.0
            elif key == 'fallback_frequency':
                # Normalize fallback frequency (0-5 fallbacks -> 1.0 to 0.0)
                value = max(0.0, 1.0 - (analysis[key] / 5.0))
            else:
                value = analysis[key]
            
            score += value * abs(weight)
            total_weight += abs(weight)
        
        # Adjust for sentiment
        sentiment_bonus = {
            'positive': 0.1,
            'neutral': 0.0,
            'negative': -0.1
        }
        score += sentiment_bonus.get(analysis['sentiment'], 0.0)
        
        # Normalize to 0-1 range
        final_score = max(0.0, min(1.0, score / total_weight if total_weight > 0 else 0.0))
        
        return round(final_score, 2)
    
    def _get_default_analysis(self) -> Dict:
        """Return default analysis for empty conversations."""
        return {
            'clarity_score': 0.0,
            'relevance_score': 0.0,
            'accuracy_score': 0.0,
            'completeness_score': 0.0,
            'sentiment': 'neutral',
            'empathy_score': 0.0,
            'response_time_avg': 0.0,
            'resolution': False,
            'escalation_need': False,
            'fallback_frequency': 0,
            'overall_score': 0.0,
        }

