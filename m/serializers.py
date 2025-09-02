"""
Django REST Framework serializers for AI Chatbot API
"""

from rest_framework import serializers
from .models import (
    ChatSession, ChatMessage, MessageRating, WebSearchQuery,
    AIModelConfig, FineTuningJob, DailyMetrics
)


class ChatSessionSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = [
            'id', 'session_id', 'language', 'message_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'session_id', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()


class MessageRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageRating
        fields = ['rating', 'feedback', 'created_at']
        read_only_fields = ['created_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    rating = MessageRatingSerializer(source='messagerating', read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'message_type', 'content', 'topic', 'language',
            'model_used', 'confidence_score', 'response_time_ms',
            'rating', 'created_at'
        ]
        read_only_fields = [
            'id', 'model_used', 'confidence_score', 'response_time_ms', 'created_at'
        ]


class WebSearchQuerySerializer(serializers.ModelSerializer):
    results_count = serializers.SerializerMethodField()

    class Meta:
        model = WebSearchQuery
        fields = [
            'id', 'query', 'language', 'topic', 'search_results',
            'avg_rating', 'search_count', 'results_count',
            'last_searched', 'created_at'
        ]
        read_only_fields = [
            'id', 'avg_rating', 'search_count', 'last_searched', 'created_at'
        ]

    def get_results_count(self, obj):
        return len(obj.search_results) if obj.search_results else 0


class AIModelConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModelConfig
        fields = [
            'id', 'model_name', 'model_type', 'config_params',
            'avg_response_time', 'avg_rating', 'total_uses',
            'supports_tamil', 'supports_english', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'avg_response_time', 'avg_rating', 'total_uses',
            'created_at', 'updated_at'
        ]


class FineTuningJobSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model_config.model_name', read_only=True)
    improvement = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = FineTuningJob
        fields = [
            'id', 'model_name', 'training_data_count', 'status',
            'baseline_accuracy', 'improved_accuracy', 'improvement',
            'training_params', 'duration', 'error_message',
            'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'model_name', 'improvement', 'duration',
            'started_at', 'completed_at', 'created_at'
        ]

    def get_improvement(self, obj):
        if obj.baseline_accuracy and obj.improved_accuracy:
            return obj.improved_accuracy - obj.baseline_accuracy
        return None

    def get_duration(self, obj):
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return duration.total_seconds()
        return None


class DailyMetricsSerializer(serializers.ModelSerializer):
    total_rating_count = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()

    class Meta:
        model = DailyMetrics
        fields = [
            'date', 'total_messages', 'tamil_messages', 'english_messages',
            'avg_daily_rating', 'total_rating_count', 'low_rating_count',
            'avg_response_time', 'successful_responses', 'failed_responses',
            'success_rate', 'topic_distribution', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_total_rating_count(self, obj):
        return obj.low_rating_count + (obj.successful_responses - obj.low_rating_count)

    def get_success_rate(self, obj):
        total = obj.successful_responses + obj.failed_responses
        if total > 0:
            return (obj.successful_responses / total) * 100
        return 0


class MetricsSummarySerializer(serializers.Serializer):
    """Serializer for metrics summary data"""
    period = serializers.DictField()
    charts = serializers.DictField()
    summary = serializers.DictField()


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat API requests"""
    message = serializers.CharField(max_length=2000)
    session_id = serializers.CharField(max_length=100)
    language = serializers.ChoiceField(choices=[('en', 'English'), ('ta', 'Tamil')])
    topic = serializers.CharField(max_length=20, required=False, default='general')


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat API responses"""
    user_message = serializers.DictField()
    ai_response = serializers.DictField()
    topic = serializers.CharField()
    detected_language = serializers.CharField()


class RatingRequestSerializer(serializers.Serializer):
    """Serializer for message rating requests"""
    message_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(max_length=1000, required=False, allow_blank=True)


class SearchRequestSerializer(serializers.Serializer):
    """Serializer for web search requests"""
    q = serializers.CharField(max_length=500)
    lang = serializers.ChoiceField(
        choices=[('en', 'English'), ('ta', 'Tamil')], 
        default='en'
    )
    topic = serializers.CharField(max_length=20, default='general')


class TranslationRequestSerializer(serializers.Serializer):
    """Serializer for translation requests"""
    text = serializers.CharField(max_length=2000)
    target_lang = serializers.ChoiceField(
        choices=[('en', 'English'), ('ta', 'Tamil')],
        default='ta'
    )
    source_lang = serializers.CharField(max_length=2, default='auto')


class TranslationResponseSerializer(serializers.Serializer):
    """Serializer for translation responses"""
    original_text = serializers.CharField()
    translated_text = serializers.CharField()
    source_language = serializers.CharField()
    target_language = serializers.CharField()
