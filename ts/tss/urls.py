from django.urls import path,include 
from tss.views import *


urlpatterns = [
    
    path ('',views.index,name='joke'),
    path('greeks/', option_price_view, name='option_price'),
 
   
 
   
]
