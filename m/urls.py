"""
URL configuration for AI Chatbot app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'ai_chatbot'

urlpatterns = [
    # Web interface
    path('', views.ChatInterfaceView.as_view(), name='chat_interface'),

    # API endpoints
    path('api/chat/', views.ChatAPIView.as_view(), name='chat_api'),
    path('api/rate/', views.RateMessageView.as_view(), name='rate_message'),
    path('api/search/', views.SearchAPIView.as_view(), name='search_api'),
    path('api/history/', views.ChatHistoryView.as_view(), name='chat_history'),
    path('api/metrics/', views.MetricsAPIView.as_view(), name='metrics_api'),
    path('api/translate/', views.translate_api, name='translate_api'),

    # Export functionality
    path('export/history/', views.export_chat_history, name='export_history'),
]
