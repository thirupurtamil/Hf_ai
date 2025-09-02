"""
Django admin configuration for AI Chatbot models
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import (
    ChatSession, ChatMessage, MessageRating, WebSearchQuery,
    AIModelConfig, FineTuningJob, DailyMetrics
)


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'language', 'message_count', 'created_at', 'updated_at']
    list_filter = ['language', 'created_at', 'updated_at']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['session_id', 'created_at', 'updated_at']

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Message Count'


class MessageRatingInline(admin.StackedInline):
    model = MessageRating
    extra = 0
    readonly_fields = ['created_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'session', 'message_type', 'topic', 'language', 
        'content_preview', 'confidence_score', 'rating_display', 'created_at'
    ]
    list_filter = [
        'message_type', 'topic', 'language', 'model_used', 'created_at'
    ]
    search_fields = ['content', 'session__session_id']
    readonly_fields = ['created_at']
    inlines = [MessageRatingInline]

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

    def rating_display(self, obj):
        try:
            rating = obj.messagerating.rating
            stars = '⭐' * rating + '☆' * (5 - rating)
            return f"{stars} ({rating}/5)"
        except:
            return 'No rating'
    rating_display.short_description = 'Rating'


@admin.register(MessageRating)
class MessageRatingAdmin(admin.ModelAdmin):
    list_display = ['message', 'rating', 'star_display', 'feedback_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['feedback', 'message__content']
    readonly_fields = ['created_at']

    def star_display(self, obj):
        return '⭐' * obj.rating + '☆' * (5 - obj.rating)
    star_display.short_description = 'Stars'

    def feedback_preview(self, obj):
        if obj.feedback:
            return obj.feedback[:50] + '...' if len(obj.feedback) > 50 else obj.feedback
        return 'No feedback'
    feedback_preview.short_description = 'Feedback'


@admin.register(WebSearchQuery)
class WebSearchQueryAdmin(admin.ModelAdmin):
    list_display = [
        'query_preview', 'language', 'topic', 'avg_rating', 
        'search_count', 'results_count', 'last_searched'
    ]
    list_filter = ['language', 'topic', 'last_searched', 'created_at']
    search_fields = ['query']
    readonly_fields = ['created_at', 'last_searched']

    def query_preview(self, obj):
        return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
    query_preview.short_description = 'Query'

    def results_count(self, obj):
        return len(obj.search_results) if obj.search_results else 0
    results_count.short_description = 'Results Count'

    def view_results(self, obj):
        if obj.search_results:
            return format_html(
                '<a href="#" onclick="alert(\'{}\')">{} results</a>',
                json.dumps(obj.search_results, indent=2)[:500],
                len(obj.search_results)
            )
        return 'No results'
    view_results.short_description = 'Search Results'


@admin.register(AIModelConfig)
class AIModelConfigAdmin(admin.ModelAdmin):
    list_display = [
        'model_name', 'model_type', 'avg_rating', 'total_uses',
        'avg_response_time', 'language_support', 'is_active'
    ]
    list_filter = ['model_type', 'is_active', 'supports_tamil', 'supports_english']
    search_fields = ['model_name']
    readonly_fields = ['created_at', 'updated_at']

    def language_support(self, obj):
        languages = []
        if obj.supports_tamil:
            languages.append('Tamil')
        if obj.supports_english:
            languages.append('English')
        return ', '.join(languages) if languages else 'None'
    language_support.short_description = 'Languages'


@admin.register(FineTuningJob)
class FineTuningJobAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'model_config', 'status', 'training_data_count',
        'baseline_accuracy', 'improved_accuracy', 'improvement_display',
        'started_at', 'completed_at'
    ]
    list_filter = ['status', 'started_at', 'completed_at']
    readonly_fields = ['created_at', 'started_at', 'completed_at']

    def improvement_display(self, obj):
        if obj.baseline_accuracy and obj.improved_accuracy:
            improvement = obj.improved_accuracy - obj.baseline_accuracy
            if improvement > 0:
                return format_html(
                    '<span style="color: green;">+{:.2f}</span>',
                    improvement
                )
            elif improvement < 0:
                return format_html(
                    '<span style="color: red;">{:.2f}</span>',
                    improvement
                )
            else:
                return '0.00'
        return 'N/A'
    improvement_display.short_description = 'Improvement'


@admin.register(DailyMetrics)
class DailyMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_messages', 'language_breakdown', 'avg_daily_rating',
        'avg_response_time', 'success_rate', 'low_rating_count'
    ]
    list_filter = ['date', 'avg_daily_rating']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'

    def language_breakdown(self, obj):
        return f"TA: {obj.tamil_messages}, EN: {obj.english_messages}"
    language_breakdown.short_description = 'Tamil/English'

    def success_rate(self, obj):
        total = obj.successful_responses + obj.failed_responses
        if total > 0:
            rate = (obj.successful_responses / total) * 100
            return f"{rate:.1f}%"
        return 'N/A'
    success_rate.short_description = 'Success Rate'

    def view_topic_distribution(self, obj):
        if obj.topic_distribution:
            return mark_safe(
                '<pre>' + json.dumps(obj.topic_distribution, indent=2) + '</pre>'
            )
        return 'No data'
    view_topic_distribution.short_description = 'Topic Distribution'


# Custom admin site header
admin.site.site_header = "Mobile AI Django Administration"
admin.site.site_title = "AI Chatbot Admin"
admin.site.index_title = "Welcome to AI Chatbot Administration"

# Add custom CSS for admin
class AdminConfig:
    def ready(self):
        admin.site.enable_nav_sidebar = False

        # Custom CSS
        admin.site.extra_css = [
            'admin/css/custom_admin.css'
        ]
