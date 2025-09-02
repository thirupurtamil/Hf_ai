"""
Main URL configuration for mobile_ai_django project
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ai_chatbot.urls')),
    path('api/', include('ai_chatbot.urls')),

    # Redirect root to chat interface
    path('chat/', RedirectView.as_view(url='/', permanent=False)),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site customization
admin.site.site_header = "Mobile AI Django Admin"
admin.site.site_title = "AI Chatbot"
admin.site.index_title = "AI Chatbot Administration"
