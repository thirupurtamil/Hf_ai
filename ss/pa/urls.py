from django.urls import path,include 
from pa import views


urlpatterns = [
    
    path ('get_pa/',views.pa,name='pa'),
    path ('get_ps/',views.pa,name='ps'),

    
    
   
 
   
]