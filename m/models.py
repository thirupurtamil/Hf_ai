"""
AI Chatbot models for multi-language support with Tamil and English
Includes chat history, ratings, and auto fine-tuning data
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import json


class ChatSession(models.Model):
    """Chat session to group related messages"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    language = models.CharField(
        max_length=2,
        choices=[('en', 'English'), ('ta', 'Tamil')],
        default='ta'
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Session {self.session_id} - {self.language}"


class ChatMessage(models.Model):
    """Individual chat messages with multilingual support"""

    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('ai', 'AI Response'),
        ('system', 'System Message'),
    ]

    TOPIC_CHOICES = [
        ('garments', _('Garments')),
        ('share_market', _('Share Market')),
        ('ai_tools', _('AI Tools')),
        ('python', _('Python Programming')),
        ('java', _('Java Programming')),
        ('html', _('HTML/Web Development')),
        ('embedded_system', _('Embedded Systems')),
        ('raspberry_pi', _('Raspberry Pi')),
        ('linux', _('Linux')),
        ('general', _('General')),
    ]

    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES, default='general')
    language = models.CharField(max_length=2, choices=[('en', 'English'), ('ta', 'Tamil')])

    # AI response metadata
    model_used = models.CharField(max_length=50, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."


class MessageRating(models.Model):
    """User ratings for AI responses to improve model"""

    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]

    message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Rating {self.rating}/5 for message {self.message.id}"


class WebSearchQuery(models.Model):
    """Store web search queries and results for training data"""

    query = models.TextField()
    language = models.CharField(max_length=2, choices=[('en', 'English'), ('ta', 'Tamil')])
    topic = models.CharField(max_length=20, choices=ChatMessage.TOPIC_CHOICES)
    search_results = models.JSONField(default=list)
    avg_rating = models.FloatField(default=0.0)
    search_count = models.IntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_searched']
        unique_together = ['query', 'language', 'topic']

    def __str__(self):
        return f"{self.query[:50]} - {self.language} ({self.avg_rating}/5)"


class AIModelConfig(models.Model):
    """Configuration for different AI models and their performance"""

    model_name = models.CharField(max_length=100, unique=True)
    model_type = models.CharField(
        max_length=20,
        choices=[
            ('openai', 'OpenAI GPT'),
            ('huggingface', 'Hugging Face'),
            ('local', 'Local Model'),
        ]
    )

    # Model parameters stored as JSON
    config_params = models.JSONField(default=dict)

    # Performance metrics
    avg_response_time = models.FloatField(default=0.0)
    avg_rating = models.FloatField(default=0.0)
    total_uses = models.IntegerField(default=0)

    # Language support
    supports_tamil = models.BooleanField(default=False)
    supports_english = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-avg_rating', '-total_uses']

    def __str__(self):
        return f"{self.model_name} - Rating: {self.avg_rating}/5"


class FineTuningJob(models.Model):
    """Track fine-tuning jobs and their results"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    model_config = models.ForeignKey(AIModelConfig, on_delete=models.CASCADE)
    training_data_count = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Performance before and after fine-tuning
    baseline_accuracy = models.FloatField(null=True, blank=True)
    improved_accuracy = models.FloatField(null=True, blank=True)

    # Training parameters
    training_params = models.JSONField(default=dict)

    # Job metadata
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Fine-tune {self.model_config.model_name} - {self.status}"


class DailyMetrics(models.Model):
    """Daily metrics for monitoring system performance"""

    date = models.DateField(unique=True)

    # Message statistics
    total_messages = models.IntegerField(default=0)
    tamil_messages = models.IntegerField(default=0)
    english_messages = models.IntegerField(default=0)

    # Rating statistics
    avg_daily_rating = models.FloatField(default=0.0)
    low_rating_count = models.IntegerField(default=0)  # Ratings below threshold

    # Performance metrics
    avg_response_time = models.FloatField(default=0.0)
    successful_responses = models.IntegerField(default=0)
    failed_responses = models.IntegerField(default=0)

    # Topic distribution (JSON field)
    topic_distribution = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Metrics for {self.date} - Rating: {self.avg_daily_rating}/5"
