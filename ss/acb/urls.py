from django.urls import path,include 
from acb import views

from django.conf.urls import handler404, handler500

handler500 = 'acb.views.error_500'
handler404 = 'acb.views.error_404'




urlpatterns = [
    
    path ('home',views.acb,name='home'),
    path ('oi',views.ch,name='oi'),
   
    
    
   
 
   
]