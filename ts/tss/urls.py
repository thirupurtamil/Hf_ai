from django.urls import path,include 
from tss import views 


urlpatterns = [
    
    path ('',views.index,name='joke'),
    path('greeks/', views.option_price_view, name='option_price'),
 
   
 
   
]
