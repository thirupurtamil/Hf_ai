from django.urls import path,include 
from nfy import views


urlpatterns = [
    
    path ('get_nfy/',views.nfy,name='nfy'),
    path ('chart',views.chart,name='chart'),
    
    
    
   
 
   
]