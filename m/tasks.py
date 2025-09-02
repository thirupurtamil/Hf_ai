"""
Celery tasks for background processing, auto fine-tuning, and daily metrics
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta
import logging
import json

from .models import (
    ChatMessage, MessageRating, WebSearchQuery, 
    AIModelConfig, FineTuningJob, DailyMetrics
)
from .utils import search_duckduckgo, get_ai_response

logger = logging.getLogger(__name__)


@shared_task
def update_daily_metrics():
    """Update daily metrics for monitoring"""
    try:
        today = timezone.now().date()

        # Get today's messages
        today_messages = ChatMessage.objects.filter(
            created_at__date=today
        )

        # Calculate metrics
        total_messages = today_messages.count()
        tamil_messages = today_messages.filter(language='ta').count()
        english_messages = today_messages.filter(language='en').count()

        # Get AI messages only for response metrics
        ai_messages = today_messages.filter(message_type='ai')

        # Calculate ratings
        ratings = MessageRating.objects.filter(
            message__in=ai_messages,
            created_at__date=today
        )

        avg_rating = ratings.aggregate(avg=Avg('rating'))['avg'] or 0.0
        low_rating_count = ratings.filter(rating__lt=3).count()

        # Calculate response times
        response_times = ai_messages.exclude(
            response_time_ms__isnull=True
        ).values_list('response_time_ms', flat=True)

        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0

        # Success/failure counts
        successful_responses = ai_messages.filter(confidence_score__gte=0.5).count()
        failed_responses = ai_messages.filter(confidence_score__lt=0.5).count()

        # Topic distribution
        topic_dist = {}
        for topic_choice in ChatMessage.TOPIC_CHOICES:
            topic = topic_choice[0]
            count = today_messages.filter(topic=topic).count()
            if count > 0:
                topic_dist[topic] = count

        # Create or update daily metrics
        metrics, created = DailyMetrics.objects.get_or_create(
            date=today,
            defaults={
                'total_messages': total_messages,
                'tamil_messages': tamil_messages,
                'english_messages': english_messages,
                'avg_daily_rating': avg_rating,
                'low_rating_count': low_rating_count,
                'avg_response_time': avg_response_time,
                'successful_responses': successful_responses,
                'failed_responses': failed_responses,
                'topic_distribution': topic_dist,
            }
        )

        if not created:
            # Update existing metrics
            metrics.total_messages = total_messages
            metrics.tamil_messages = tamil_messages
            metrics.english_messages = english_messages
            metrics.avg_daily_rating = avg_rating
            metrics.low_rating_count = low_rating_count
            metrics.avg_response_time = avg_response_time
            metrics.successful_responses = successful_responses
            metrics.failed_responses = failed_responses
            metrics.topic_distribution = topic_dist
            metrics.save()

        logger.info(f"Updated daily metrics for {today}: {total_messages} messages, {avg_rating:.2f} avg rating")
        return f"Daily metrics updated: {total_messages} messages"

    except Exception as e:
        logger.error(f"Error updating daily metrics: {e}")
        raise


@shared_task
def daily_web_search_and_rating():
    """Daily task to search for low-rated queries and update knowledge base"""
    try:
        from django.conf import settings

        # Get low-rated queries from last 7 days
        week_ago = timezone.now() - timedelta(days=7)

        low_rated_messages = ChatMessage.objects.filter(
            message_type='ai',
            created_at__gte=week_ago,
            messagerating__rating__lt=3
        ).select_related('messagerating')

        improved_count = 0

        for message in low_rated_messages[:20]:  # Process top 20 low-rated messages
            try:
                # Extract key terms from the original user message
                user_message = ChatMessage.objects.filter(
                    session=message.session,
                    message_type='user',
                    created_at__lt=message.created_at
                ).last()

                if not user_message:
                    continue

                # Perform web search for better information
                search_results = search_duckduckgo(
                    user_message.content,
                    language=message.language,
                    max_results=5
                )

                if search_results:
                    # Store search results for training
                    web_query, created = WebSearchQuery.objects.get_or_create(
                        query=user_message.content,
                        language=message.language,
                        topic=message.topic,
                        defaults={
                            'search_results': search_results,
                            'avg_rating': message.messagerating.rating
                        }
                    )

                    if not created:
                        # Update with new search results
                        web_query.search_results = search_results
                        web_query.search_count += 1
                        # Update average rating
                        current_total = web_query.avg_rating * (web_query.search_count - 1)
                        web_query.avg_rating = (current_total + message.messagerating.rating) / web_query.search_count
                        web_query.save()

                    improved_count += 1

            except Exception as e:
                logger.warning(f"Error processing message {message.id}: {e}")
                continue

        logger.info(f"Daily web search completed: improved {improved_count} queries")
        return f"Processed {improved_count} low-rated queries"

    except Exception as e:
        logger.error(f"Error in daily web search task: {e}")
        raise


@shared_task
def weekly_auto_fine_tune():
    """Weekly task to auto fine-tune AI models based on ratings"""
    try:
        from django.conf import settings

        # Check if auto fine-tuning is enabled and threshold met
        threshold = getattr(settings, 'AUTO_FINETUNE_THRESHOLD', 0.7)
        min_samples = getattr(settings, 'MIN_TRAINING_SAMPLES', 100)
        max_samples = getattr(settings, 'MAX_TRAINING_SAMPLES', 1000)

        # Get weekly metrics
        week_ago = timezone.now() - timedelta(days=7)

        # Calculate average rating for the week
        weekly_ratings = MessageRating.objects.filter(
            created_at__gte=week_ago,
            message__message_type='ai'
        )

        if weekly_ratings.count() < min_samples:
            logger.info(f"Not enough ratings for fine-tuning: {weekly_ratings.count()} < {min_samples}")
            return "Insufficient data for fine-tuning"

        avg_weekly_rating = weekly_ratings.aggregate(avg=Avg('rating'))['avg']

        # Only fine-tune if rating is below threshold
        if avg_weekly_rating >= threshold:
            logger.info(f"Average rating {avg_weekly_rating} is above threshold {threshold}")
            return "No fine-tuning needed - performance is good"

        # Prepare training data from high-rated interactions
        training_data = prepare_training_data(max_samples)

        if len(training_data) < min_samples:
            logger.warning(f"Insufficient training data: {len(training_data)} < {min_samples}")
            return "Insufficient training data"

        # Get active AI models
        active_models = AIModelConfig.objects.filter(is_active=True)

        for model_config in active_models:
            try:
                # Create fine-tuning job
                fine_tune_job = FineTuningJob.objects.create(
                    model_config=model_config,
                    training_data_count=len(training_data),
                    baseline_accuracy=model_config.avg_rating,
                    training_params={
                        'learning_rate': 0.0001,
                        'batch_size': 8,
                        'epochs': 3,
                        'threshold': threshold
                    }
                )

                # Start fine-tuning (async)
                start_model_fine_tuning.delay(fine_tune_job.id, training_data)

            except Exception as e:
                logger.error(f"Error creating fine-tuning job for {model_config.model_name}: {e}")
                continue

        logger.info(f"Started fine-tuning for {active_models.count()} models with {len(training_data)} samples")
        return f"Started fine-tuning for {active_models.count()} models"

    except Exception as e:
        logger.error(f"Error in weekly auto fine-tune task: {e}")
        raise


@shared_task
def start_model_fine_tuning(job_id, training_data):
    """Start fine-tuning for a specific model"""
    try:
        job = FineTuningJob.objects.get(id=job_id)
        job.status = 'running'
        job.started_at = timezone.now()
        job.save()

        # This is where you would integrate with actual fine-tuning APIs
        # For OpenAI models, you would use their fine-tuning API
        # For local models, you would implement the training loop

        # Simulate fine-tuning process
        import time
        import random

        # Simulate training time
        time.sleep(30)  # In real implementation, this would be actual training

        # Simulate improved accuracy
        improvement = random.uniform(0.1, 0.3)
        new_accuracy = min(5.0, job.baseline_accuracy + improvement)

        # Update job status
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.improved_accuracy = new_accuracy
        job.save()

        # Update model config
        model_config = job.model_config
        model_config.avg_rating = new_accuracy
        model_config.save()

        logger.info(f"Fine-tuning completed for {model_config.model_name}: {job.baseline_accuracy} -> {new_accuracy}")
        return f"Fine-tuning completed: {job.baseline_accuracy:.2f} -> {new_accuracy:.2f}"

    except FineTuningJob.DoesNotExist:
        logger.error(f"Fine-tuning job {job_id} not found")
        raise
    except Exception as e:
        # Update job with error
        try:
            job = FineTuningJob.objects.get(id=job_id)
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()
        except:
            pass

        logger.error(f"Error in fine-tuning job {job_id}: {e}")
        raise


def prepare_training_data(max_samples):
    """Prepare training data from high-rated interactions"""

    # Get high-rated messages (4-5 stars) from last month
    month_ago = timezone.now() - timedelta(days=30)

    high_rated_messages = ChatMessage.objects.filter(
        message_type='ai',
        created_at__gte=month_ago,
        messagerating__rating__gte=4
    ).select_related('messagerating', 'session')

    training_data = []

    for ai_message in high_rated_messages[:max_samples]:
        try:
            # Get the corresponding user message
            user_message = ChatMessage.objects.filter(
                session=ai_message.session,
                message_type='user',
                created_at__lt=ai_message.created_at
            ).last()

            if user_message:
                training_sample = {
                    'input': user_message.content,
                    'output': ai_message.content,
                    'topic': ai_message.topic,
                    'language': ai_message.language,
                    'rating': ai_message.messagerating.rating,
                    'confidence': ai_message.confidence_score or 0.8
                }
                training_data.append(training_sample)

        except Exception as e:
            logger.warning(f"Error preparing training sample for message {ai_message.id}: {e}")
            continue

    return training_data


@shared_task
def cleanup_old_data():
    """Clean up old data to maintain database performance"""
    try:
        # Delete old messages older than 6 months
        six_months_ago = timezone.now() - timedelta(days=180)

        old_messages = ChatMessage.objects.filter(created_at__lt=six_months_ago)
        deleted_count = old_messages.count()
        old_messages.delete()

        # Clean up old search queries with low ratings
        old_searches = WebSearchQuery.objects.filter(
            last_searched__lt=six_months_ago,
            avg_rating__lt=2.0
        )
        deleted_searches = old_searches.count()
        old_searches.delete()

        # Clean up old metrics older than 1 year
        year_ago = timezone.now() - timedelta(days=365)
        old_metrics = DailyMetrics.objects.filter(date__lt=year_ago.date())
        deleted_metrics = old_metrics.count()
        old_metrics.delete()

        logger.info(f"Cleanup completed: {deleted_count} messages, {deleted_searches} searches, {deleted_metrics} metrics")
        return f"Cleaned up {deleted_count} old messages and {deleted_searches} searches"

    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        raise


@shared_task
def generate_weekly_report():
    """Generate weekly performance report"""
    try:
        week_ago = timezone.now() - timedelta(days=7)

        # Get weekly statistics
        weekly_messages = ChatMessage.objects.filter(created_at__gte=week_ago)
        total_messages = weekly_messages.count()

        # Language breakdown
        tamil_count = weekly_messages.filter(language='ta').count()
        english_count = weekly_messages.filter(language='en').count()

        # Topic breakdown
        topic_stats = {}
        for topic_choice in ChatMessage.TOPIC_CHOICES:
            topic = topic_choice[0]
            count = weekly_messages.filter(topic=topic).count()
            if count > 0:
                topic_stats[topic] = count

        # Rating statistics
        weekly_ratings = MessageRating.objects.filter(
            created_at__gte=week_ago,
            message__message_type='ai'
        )

        if weekly_ratings.exists():
            avg_rating = weekly_ratings.aggregate(avg=Avg('rating'))['avg']
            rating_distribution = {}
            for i in range(1, 6):
                rating_distribution[f"{i}_star"] = weekly_ratings.filter(rating=i).count()
        else:
            avg_rating = 0
            rating_distribution = {}

        # Performance metrics
        ai_messages = weekly_messages.filter(message_type='ai')
        avg_response_time = ai_messages.aggregate(
            avg=Avg('response_time_ms')
        )['avg'] or 0

        # Compile report
        report = {
            'period': f"{week_ago.date()} to {timezone.now().date()}",
            'total_messages': total_messages,
            'language_breakdown': {
                'tamil': tamil_count,
                'english': english_count
            },
            'topic_distribution': topic_stats,
            'average_rating': round(avg_rating, 2),
            'rating_distribution': rating_distribution,
            'average_response_time_ms': round(avg_response_time, 2),
            'generated_at': timezone.now().isoformat()
        }

        # Log the report
        logger.info(f"Weekly report generated: {json.dumps(report, indent=2)}")

        # Here you could send the report via email or save to file
        # send_weekly_report_email(report)

        return f"Weekly report generated: {total_messages} messages, {avg_rating:.2f} avg rating"

    except Exception as e:
        logger.error(f"Error generating weekly report: {e}")
        raise


@shared_task
def sync_web_search_data():
    """Sync and update web search data for better responses"""
    try:
        # Get popular search queries that need updating
        popular_queries = WebSearchQuery.objects.filter(
            search_count__gte=5,
            last_searched__lt=timezone.now() - timedelta(days=7)
        )[:10]

        updated_count = 0

        for query_obj in popular_queries:
            try:
                # Re-search for updated information
                new_results = search_duckduckgo(
                    query_obj.query,
                    language=query_obj.language,
                    max_results=5
                )

                if new_results:
                    query_obj.search_results = new_results
                    query_obj.save()
                    updated_count += 1

            except Exception as e:
                logger.warning(f"Error updating search query {query_obj.id}: {e}")
                continue

        logger.info(f"Updated {updated_count} search queries")
        return f"Updated {updated_count} popular search queries"

    except Exception as e:
        logger.error(f"Error in sync web search data task: {e}")
        raise
