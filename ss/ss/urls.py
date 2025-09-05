from django.urls import path, include 




urlpatterns = [
    
    path('', include('pre_open.urls')),
    path('', include('homepage.urls')),
    path('', include('nifty.urls')),
    path('', include('acb.urls')),
    path('', include('home.urls')),
    path('', include('pa.urls')),
    path('', include('nfy.urls')),
    path('', include('ts1.urls')),
]

    



