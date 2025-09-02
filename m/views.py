"""
AI Chatbot Views with Tamil/English support and DuckDuckGo integration
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Avg, Count, Q
from django.utils.translation import gettext as _, activate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    ChatSession, ChatMessage, MessageRating, 
    WebSearchQuery, AIModelConfig, DailyMetrics
)
from .utils import (
    get_ai_response, translate_text, search_duckduckgo,
    detect_language, get_topic_from_text
)
from .tasks import update_daily_metrics


class ChatInterfaceView(TemplateView):
    """Main chat interface"""
    template_name = 'ai_chatbot/chat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get or create session
        session_id = self.request.session.get('chat_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            self.request.session['chat_session_id'] = session_id

        chat_session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                'user': self.request.user if self.request.user.is_authenticated else None,
                'language': 'ta'  # Default to Tamil
            }
        )

        # Get recent messages
        recent_messages = ChatMessage.objects.filter(
            session=chat_session
        ).order_by('created_at')[:50]

        context.update({
            'session': chat_session,
            'messages': recent_messages,
            'supported_topics': ChatMessage.TOPIC_CHOICES,
        })
        return context


class ChatAPIView(APIView):
    """API endpoint for chat interactions"""

    def post(self, request):
        try:
            data = request.data
            message_text = data.get('message', '').strip()
            session_id = data.get('session_id')
            language = data.get('language', 'ta')

            if not message_text or not session_id:
                return Response({
                    'error': 'Message and session_id are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get or create chat session
            chat_session, created = ChatSession.objects.get_or_create(
                session_id=session_id,
                defaults={
                    'user': request.user if request.user.is_authenticated else None,
                    'language': language
                }
            )

            # Update session language if changed
            if chat_session.language != language:
                chat_session.language = language
                chat_session.save()

            # Detect topic and actual language
            detected_lang = detect_language(message_text)
            topic = get_topic_from_text(message_text)

            # Save user message
            user_message = ChatMessage.objects.create(
                session=chat_session,
                message_type='user',
                content=message_text,
                topic=topic,
                language=detected_lang or language
            )

            # Get AI response
            start_time = time.time()
            ai_response_data = get_ai_response(
                message_text, 
                language=language,
                topic=topic,
                session_history=chat_session.messages.all()[:10]
            )
            response_time = int((time.time() - start_time) * 1000)

            # Save AI response
            ai_message = ChatMessage.objects.create(
                session=chat_session,
                message_type='ai',
                content=ai_response_data['response'],
                topic=topic,
                language=language,
                model_used=ai_response_data.get('model_used', 'unknown'),
                confidence_score=ai_response_data.get('confidence', 0.0),
                response_time_ms=response_time
            )

            # Prepare response
            response_data = {
                'user_message': {
                    'id': user_message.id,
                    'content': user_message.content,
                    'timestamp': user_message.created_at.isoformat()
                },
                'ai_response': {
                    'id': ai_message.id,
                    'content': ai_message.content,
                    'timestamp': ai_message.created_at.isoformat(),
                    'model_used': ai_message.model_used,
                    'confidence': ai_message.confidence_score,
                    'response_time_ms': response_time
                },
                'topic': topic,
                'detected_language': detected_lang
            }

            # Trigger metrics update
            update_daily_metrics.delay()

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': f'Internal server error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RateMessageView(APIView):
    """Rate AI responses for improvement"""

    def post(self, request):
        try:
            data = request.data
            message_id = data.get('message_id')
            rating = data.get('rating')
            feedback = data.get('feedback', '')

            if not message_id or not rating:
                return Response({
                    'error': 'message_id and rating are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            if rating not in [1, 2, 3, 4, 5]:
                return Response({
                    'error': 'Rating must be between 1 and 5'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                message = ChatMessage.objects.get(
                    id=message_id, 
                    message_type='ai'
                )
            except ChatMessage.DoesNotExist:
                return Response({
                    'error': 'AI message not found'
                }, status=status.HTTP_404_NOT_FOUND)

            # Create or update rating
            rating_obj, created = MessageRating.objects.get_or_create(
                message=message,
                defaults={
                    'rating': rating,
                    'feedback': feedback
                }
            )

            if not created:
                rating_obj.rating = rating
                rating_obj.feedback = feedback
                rating_obj.save()

            return Response({
                'message': 'Rating saved successfully',
                'rating_id': rating_obj.id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': f'Internal server error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchAPIView(APIView):
    """DuckDuckGo search integration"""

    def get(self, request):
        try:
            query = request.query_params.get('q', '').strip()
            language = request.query_params.get('lang', 'ta')
            topic = request.query_params.get('topic', 'general')

            if not query:
                return Response({
                    'error': 'Query parameter q is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Search using DuckDuckGo
            search_results = search_duckduckgo(query, language=language)

            # Store/update search query
            web_query, created = WebSearchQuery.objects.get_or_create(
                query=query,
                language=language,
                topic=topic,
                defaults={'search_results': search_results}
            )

            if not created:
                web_query.search_results = search_results
                web_query.search_count += 1
                web_query.save()

            return Response({
                'query': query,
                'language': language,
                'topic': topic,
                'results': search_results,
                'total_results': len(search_results)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': f'Search error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatHistoryView(APIView):
    """Get chat history for a session"""

    def get(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({
                'error': 'session_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            chat_session = ChatSession.objects.get(session_id=session_id)
            messages = ChatMessage.objects.filter(
                session=chat_session
            ).order_by('created_at')

            history = []
            for msg in messages:
                msg_data = {
                    'id': msg.id,
                    'type': msg.message_type,
                    'content': msg.content,
                    'topic': msg.topic,
                    'language': msg.language,
                    'timestamp': msg.created_at.isoformat(),
                }

                if msg.message_type == 'ai':
                    msg_data.update({
                        'model_used': msg.model_used,
                        'confidence': msg.confidence_score,
                        'response_time_ms': msg.response_time_ms,
                    })

                    # Add rating if exists
                    try:
                        rating = MessageRating.objects.get(message=msg)
                        msg_data['rating'] = {
                            'score': rating.rating,
                            'feedback': rating.feedback
                        }
                    except MessageRating.DoesNotExist:
                        msg_data['rating'] = None

                history.append(msg_data)

            return Response({
                'session_id': session_id,
                'language': chat_session.language,
                'message_count': len(history),
                'messages': history
            }, status=status.HTTP_200_OK)

        except ChatSession.DoesNotExist:
            return Response({
                'error': 'Chat session not found'
            }, status=status.HTTP_404_NOT_FOUND)


class MetricsAPIView(APIView):
    """API for dashboard metrics and charts"""

    def get(self, request):
        # Get date range
        days = int(request.query_params.get('days', 7))
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)

        # Get daily metrics
        daily_metrics = DailyMetrics.objects.filter(
            date__range=[start_date, end_date]
        ).order_by('date')

        # Prepare chart data
        dates = []
        message_counts = []
        rating_averages = []
        response_times = []
        language_distribution = {'tamil': 0, 'english': 0}
        topic_distribution = {}

        for metric in daily_metrics:
            dates.append(metric.date.strftime('%Y-%m-%d'))
            message_counts.append(metric.total_messages)
            rating_averages.append(metric.avg_daily_rating)
            response_times.append(metric.avg_response_time)

            # Language distribution
            language_distribution['tamil'] += metric.tamil_messages
            language_distribution['english'] += metric.english_messages

            # Topic distribution
            for topic, count in metric.topic_distribution.items():
                topic_distribution[topic] = topic_distribution.get(topic, 0) + count

        # Overall statistics
        total_messages = sum(message_counts)
        avg_rating = sum(rating_averages) / len(rating_averages) if rating_averages else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Low rating queries for improvement
        low_rating_messages = ChatMessage.objects.filter(
            messagerating__rating__lt=3,
            created_at__date__range=[start_date, end_date]
        ).select_related('messagerating')[:10]

        improvement_suggestions = []
        for msg in low_rating_messages:
            improvement_suggestions.append({
                'message': msg.content[:100],
                'rating': msg.messagerating.rating,
                'feedback': msg.messagerating.feedback,
                'topic': msg.topic,
                'language': msg.language
            })

        return Response({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'charts': {
                'daily_messages': {
                    'labels': dates,
                    'data': message_counts
                },
                'daily_ratings': {
                    'labels': dates,
                    'data': rating_averages
                },
                'response_times': {
                    'labels': dates,
                    'data': response_times
                },
                'language_distribution': language_distribution,
                'topic_distribution': topic_distribution
            },
            'summary': {
                'total_messages': total_messages,
                'average_rating': round(avg_rating, 2),
                'average_response_time': round(avg_response_time, 2),
                'improvement_suggestions': improvement_suggestions
            }
        }, status=status.HTTP_200_OK)


@csrf_exempt
@require_http_methods(["POST"])
def translate_api(request):
    """Translation API endpoint"""
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        target_language = data.get('target_lang', 'ta')

        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)

        # Detect source language
        source_lang = detect_language(text)

        # Translate if needed
        if source_lang != target_language:
            translated_text = translate_text(text, target_lang=target_language)
        else:
            translated_text = text

        return JsonResponse({
            'original_text': text,
            'translated_text': translated_text,
            'source_language': source_lang,
            'target_language': target_language
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def export_chat_history(request):
    """Export chat history as CSV"""
    import csv
    from django.http import HttpResponse

    session_id = request.GET.get('session_id')
    if not session_id:
        return JsonResponse({'error': 'session_id parameter required'}, status=400)

    try:
        chat_session = ChatSession.objects.get(session_id=session_id)
        messages = ChatMessage.objects.filter(session=chat_session).order_by('created_at')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="chat_history_{session_id}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Timestamp', 'Type', 'Content', 'Topic', 'Language', 
            'Model Used', 'Confidence', 'Response Time (ms)', 'Rating'
        ])

        for msg in messages:
            rating = ''
            try:
                rating_obj = MessageRating.objects.get(message=msg)
                rating = f"{rating_obj.rating}/5"
            except MessageRating.DoesNotExist:
                pass

            writer.writerow([
                msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                msg.message_type,
                msg.content,
                msg.topic,
                msg.language,
                msg.model_used or '',
                msg.confidence_score or '',
                msg.response_time_ms or '',
                rating
            ])

        return response

    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Chat session not found'}, status=404)
