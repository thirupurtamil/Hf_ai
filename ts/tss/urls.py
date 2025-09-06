from django.urls import path,include 
from tss import views 


urlpatterns = [
    
    path('', views.index, name='index'),
    path('option/', views.option, name='option'),
]
   
 
   
