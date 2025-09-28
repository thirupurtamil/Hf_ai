from django.urls import path,include 
from home import views


urlpatterns = [
    path('acb/', views.home1, name='acb'),
    path("", views.dashboard, name="dashboard"),
    path('nifty-fallback/', views.nifty_fallback, name='nifty-fallback'),
    path('nifty/', views.nifty_view, name='nifty'),
    path('futures/', views.futures_view, name='futures'),
    path('options/', views.options_view, name='options'),
    path('contracts/', views.contracts_view, name='contracts'),
]