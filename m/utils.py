"""
Utility functions for AI integration, translation, and web search
"""

import openai
import requests
import json
import time
import re
from typing import List, Dict, Any, Optional
from django.conf import settings
from duckduckgo_search import DDGS
from googletrans import Translator
import logging

logger = logging.getLogger(__name__)

# Initialize translator
translator = Translator()

# OpenAI client setup
if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY


def detect_language(text: str) -> str:
    """Detect if text is Tamil or English"""
    try:
        # Simple detection based on Unicode ranges
        tamil_chars = sum(1 for char in text if '஀' <= char <= '௿')
        english_chars = sum(1 for char in text if char.isalpha() and char.isascii())

        if tamil_chars > english_chars:
            return 'ta'
        else:
            return 'en'
    except Exception:
        return 'en'  # Default to English


def translate_text(text: str, target_lang: str = 'ta', source_lang: str = 'auto') -> str:
    """Translate text using Google Translator"""
    try:
        if source_lang == target_lang:
            return text

        # Map language codes
        lang_map = {'ta': 'ta', 'en': 'en'}
        target = lang_map.get(target_lang, 'en')

        result = translator.translate(text, dest=target, src=source_lang)
        return result.text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text


def get_topic_from_text(text: str) -> str:
    """Extract topic from text using keyword matching"""
    text_lower = text.lower()

    # Topic keywords mapping
    topic_keywords = {
        'garments': ['garment', 'textile', 'cloth', 'fashion', 'dress', 'shirt', 'pant', 'saree'],
        'share_market': ['stock', 'share', 'market', 'trading', 'investment', 'nse', 'bse', 'equity'],
        'ai_tools': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'chatgpt', 'tool'],
        'python': ['python', 'django', 'flask', 'programming', 'code', 'script'],
        'java': ['java', 'spring', 'hibernate', 'jvm', 'android'],
        'html': ['html', 'css', 'javascript', 'web development', 'frontend', 'react', 'angular'],
        'embedded_system': ['embedded', 'microcontroller', 'arduino', 'pic', 'avr', 'stm32'],
        'raspberry_pi': ['raspberry pi', 'rpi', 'gpio', 'raspbian'],
        'linux': ['linux', 'ubuntu', 'debian', 'terminal', 'bash', 'shell'],
    }

    for topic, keywords in topic_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return topic

    return 'general'


def search_duckduckgo(query: str, language: str = 'en', max_results: int = 5) -> List[Dict]:
    """Search using DuckDuckGo API"""
    try:
        with DDGS() as ddgs:
            results = []

            # Add language hint to query
            if language == 'ta':
                query += " in tamil"

            search_results = ddgs.text(
                query, 
                region=getattr(settings, 'DUCKDUCKGO_REGION', 'wt-wt'),
                safesearch=getattr(settings, 'DUCKDUCKGO_SAFESEARCH', 'moderate'),
                max_results=max_results
            )

            for result in search_results:
                results.append({
                    'title': result.get('title', ''),
                    'body': result.get('body', ''),
                    'href': result.get('href', ''),
                })

            return results

    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return []


def get_ai_response(
    message: str, 
    language: str = 'en',
    topic: str = 'general',
    session_history: List = None
) -> Dict[str, Any]:
    """Get AI response using available models"""

    try:
        # Prepare context
        context = prepare_context(message, language, topic, session_history)

        # Try different AI models in order of preference
        ai_models = [
            ('openai_gpt', get_openai_response),
            ('local_model', get_local_model_response),
            ('fallback', get_fallback_response),
        ]

        for model_name, model_func in ai_models:
            try:
                response = model_func(context, language, topic)
                if response and response.get('response'):
                    response['model_used'] = model_name
                    return response
            except Exception as e:
                logger.warning(f"Model {model_name} failed: {e}")
                continue

        # If all models fail, return fallback
        return get_fallback_response(context, language, topic)

    except Exception as e:
        logger.error(f"AI response error: {e}")
        return {
            'response': 'I apologize, but I encountered an error. Please try again.',
            'model_used': 'error',
            'confidence': 0.0
        }


def prepare_context(message: str, language: str, topic: str, history: List = None) -> str:
    """Prepare context for AI model"""

    # System prompt based on language and topic
    if language == 'ta':
        system_prompt = f"""நீங்கள் ஒரு உதவிகரமான AI assistant ஆக செயல்படுங்கள். 
        தமிழில் பதிலளிக்கவும். {topic} பற்றிய கேள்விகளில் நிபுணத்துவம் வழங்கவும்."""
    else:
        system_prompt = f"""Act as a helpful AI assistant specialized in {topic}. 
        Provide accurate and detailed responses in English."""

    # Add conversation history if available
    context = system_prompt + "\n\n"

    if history:
        context += "Previous conversation:\n"
        for msg in history[-5:]:  # Last 5 messages for context
            context += f"{msg.message_type}: {msg.content}\n"

    context += f"\nCurrent message: {message}\n"

    return context


def get_openai_response(context: str, language: str, topic: str) -> Dict[str, Any]:
    """Get response from OpenAI GPT"""
    if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
        raise Exception("OpenAI API key not configured")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
            ],
            max_tokens=500,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content.strip()

        return {
            'response': ai_response,
            'confidence': 0.9,
            'model_used': 'openai_gpt'
        }

    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise


def get_local_model_response(context: str, language: str, topic: str) -> Dict[str, Any]:
    """Get response from local Hugging Face model"""
    try:
        # This is a placeholder for local model integration
        # You can integrate models like BERT, T5, or custom fine-tuned models

        # For now, return a topic-based response
        responses = get_topic_based_responses(topic, language)

        return {
            'response': responses.get('default', 'I can help you with that topic.'),
            'confidence': 0.7,
            'model_used': 'local_model'
        }

    except Exception as e:
        logger.error(f"Local model error: {e}")
        raise


def get_fallback_response(context: str, language: str, topic: str) -> Dict[str, Any]:
    """Fallback response when AI models fail"""

    responses = get_topic_based_responses(topic, language)

    return {
        'response': responses.get('default', 'I can help you with your question. Please provide more details.'),
        'confidence': 0.5,
        'model_used': 'fallback'
    }


def get_topic_based_responses(topic: str, language: str) -> Dict[str, str]:
    """Get predefined responses based on topic and language"""

    if language == 'ta':
        responses = {
            'garments': 'ஆடை தொழில் பற்றி உங்களுக்கு என்ன தெரிந்து கொள்ள வேண்டும்?',
            'share_market': 'பங்குச் சந்தை பற்றி விரிவான தகவல் வழங்க தயாராக உள்ளேன்.',
            'ai_tools': 'AI கருவிகள் பற்றி கேளுங்கள். உங்களுக்கு உதவ தயாராக உள்ளேன்.',
            'python': 'Python programming பற்றி கேளுங்கள்.',
            'java': 'Java programming பற்றிய உங்கள் கேள்வியை கேளுங்கள்.',
            'html': 'Web development பற்றி விவரமாக சொல்கிறேன்.',
            'embedded_system': 'Embedded systems பற்றி கேளுங்கள்.',
            'raspberry_pi': 'Raspberry Pi projects பற்றி பேசலாம்.',
            'linux': 'Linux commands மற்றும் tips பகிர்கிறேன்.',
            'default': 'உங்கள் கேள்வியை தெளிவாக கேளுங்கள்.'
        }
    else:
        responses = {
            'garments': 'I can help you with garment industry questions.',
            'share_market': 'Let me provide information about stock markets and trading.',
            'ai_tools': 'I can guide you about various AI tools and their applications.',
            'python': 'Ask me about Python programming, Django, or any related topics.',
            'java': 'I can help with Java programming questions.',
            'html': 'Let me assist with web development and HTML/CSS questions.',
            'embedded_system': 'I can provide information about embedded systems.',
            'raspberry_pi': 'Ask me about Raspberry Pi projects and tutorials.',
            'linux': 'I can help with Linux commands and system administration.',
            'default': 'Please provide more details about your question.'
        }

    return responses


def calculate_response_rating(response_time: float, confidence: float, user_rating: int = None) -> float:
    """Calculate overall response rating"""

    # Base rating from confidence
    rating = confidence * 5

    # Adjust based on response time (faster is better)
    if response_time < 1000:  # Less than 1 second
        rating += 0.5
    elif response_time > 5000:  # More than 5 seconds
        rating -= 0.5

    # User rating overrides if available
    if user_rating:
        rating = (rating + user_rating) / 2

    return min(5.0, max(1.0, rating))


def extract_keywords_for_search(text: str, language: str) -> List[str]:
    """Extract keywords from text for web search"""

    # Remove common words
    if language == 'ta':
        stop_words = ['என்ன', 'எப்படி', 'எங்கே', 'எப்போது', 'யார்', 'ஏன்']
    else:
        stop_words = ['what', 'how', 'where', 'when', 'who', 'why', 'is', 'are', 'the', 'a', 'an']

    # Clean and tokenize
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 2]

    return keywords[:5]  # Return top 5 keywords
