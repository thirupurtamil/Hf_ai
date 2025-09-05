from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from jugaad_data.nse import NSELive
from django.shortcuts import render 
from django.http import HttpResponse
import datetime 
import platform 
import time
import requests 
import pandas as pd
import numpy as np



url = 'https://www.nseindia.com/api/chart-databyindex?index=NIFTY%2050&indices=true&preopen=true'
headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
           'accept-language': 'en,gu;q=0.9,hi;q=0.8',
           'accept-encoding': 'gzip, deflate, br'}

session = requests.Session()

def da():
    request = session.get(url,headers=headers)
    cookies = dict(request.cookies)
    response = session.get(url, headers=headers,
cookies=cookies)
    data = response.json()
    
    
    return data


def pre_open(request):
    pre = da()
    pre_closeprice = pre["closePrice"]

    pre1 = pre["grapthData"]
    pre2 = pd.DataFrame(pre1)
    
    pre3 = pre2.head(600)
    pre4 = pre3.iloc[:,1:]
    
   
    
    pre_max = (pre4.max()).to_string()
    pre_min = (pre4.min()).to_string()
    
    
   
    pre_var = pre_closeprice

    data = { 'pre_max': pre_max,'pre_min':pre_min,
             'pre_closeprice':pre_closeprice,
             'pre_var' :pre_var, 
            }

    return render(request, 'pre_open.html', context = data)


def home(request):
    
    n = NSELive()
    nf = n.live_index('NIFTY 50')
   
    nf_lastprice = nf['data'][0]['lastPrice']
    nf_time = nf['timestamp']
    
    nf_open = nf['data'][0]['open']
    nf_pre_close = nf['data'][0]['previousClose']


    nf_dayhigh = nf['data'][0]['dayHigh']
    nf_daylow = nf['data'][0]['dayLow']
    
    
    
    nf_ver = format(nf_lastprice-nf_pre_close,".2f")



    
    """rs = format(rss-ni, ".2f")
    nf = format(rss-nf,".2f")
    ni = format(rss-rm,".2f")
    rm = format(rss-rl,".2f")"""
    
    
    
    
    
    data = { 'nf_open': nf_open,
              'nf_lastprice' : nf_lastprice ,
              'nf_time' : nf_time ,
              'nf_dayhigh': nf_dayhigh,
              'nf_daylow': nf_daylow,
              'nf_pre_close': nf_pre_close,
              'nf_ver':nf_ver,}
    return render(request, 'home.html', context = data)




























    
   
   
     
    








