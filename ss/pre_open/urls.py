from django.contrib import admin
from django.urls import path,include 
from pre_open import views


urlpatterns = [
    path('selvi', admin.site.urls),
    path ('home1',views.home,name='home1'),
    path ('pre_open',views.pre_open,name='pre_open'),
    
    
   
 
   
]