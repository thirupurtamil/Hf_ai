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
import json
import requests
import pandas as pd


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




def getCurrentPCR(symbol):
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol='+symbol
    headers = {
    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    'accept-encoding' : 'gzip, deflate, br',
    'accept-language' : 'en-US,en;q=0.9'
    }
    response = requests.get(url, headers=headers).content
    data = json.loads(response.decode('utf-8'))
    totCE = data['filtered']['CE']['totOI']
    totPE = data['filtered']['PE']['totOI']
   
    return (totPE/totCE)

def gs(symbol):
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol='+symbol
    headers = {
    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    'accept-encoding' : 'gzip, deflate, br',
    'accept-language' : 'en-US,en;q=0.9'
    }
    response = requests.get(url, headers=headers).content
    data = json.loads(response.decode('utf-8'))
    raj = data['records']['timestamp'].split(" ")[1]
    CE = data['filtered']['CE']
    PE = data['filtered']['PE']
   
    return raj


def md():
   
   headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',}


   with requests.session() as req:
        req.get('https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY',headers = headers)

        api_req=req.get('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY',headers = headers).json()
  
   return api_req



def getvolPCR(symbol):
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol='+symbol
    headers = {
    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    'accept-encoding' : 'gzip, deflate, br',
    'accept-language' : 'en-US,en;q=0.9'
    }
    response = requests.get(url, headers=headers).content
    data = json.loads(response.decode('utf-8'))
    totCE = data['filtered']['CE']['totVol']
    totPE = data['filtered']['PE']['totVol']
   
    return (totPE/totCE)


   
                 
     
 







            
        

def homepage(request):
    pre = da()
    pre_closeprice = pre["closePrice"]
    pre1 = pre["grapthData"]
 
    n = NSELive()
    nf = n.live_index('NIFTY 50')
   
    nf_lastprice = nf['data'][0]['lastPrice']
    nf_time = nf['timestamp']
    
    nf_open = nf['data'][0]['open']
    nf_pre_close = nf['data'][0]['previousClose']


    nf_dayhigh = nf['data'][0]['dayHigh']
    nf_daylow = nf['data'][0]['dayLow']
    
    nf_ver = format(nf_lastprice-nf_pre_close,".2f")
    nf_ph = format(nf_dayhigh-nf_open,".2f")
    nf_pl = format(nf_daylow-nf_open,".2f")
    
    pcr = getCurrentPCR('NIFTY') 
    pcr = round(pcr,2)

    raj = gs('NIFTY') 

    il = md()
    il2 = il["stocks"][0]
    nf_tamil = il2["metadata"]["strikePrice"]
    
    
    vpcr = getvolPCR('NIFTY') 
    vpcr = round(vpcr,2)
        
      
    
  
    data = { 'nf_open': nf_open,
              'nf_lastprice' : nf_lastprice ,
              'nf_time' : nf_time ,
              'nf_dayhigh': nf_dayhigh,
              'nf_daylow': nf_daylow,
              'nf_pre_close': nf_pre_close,
              'nf_ver':nf_ver,
              'nf_ph':nf_ph,
              'nf_pl':nf_pl,
              'nf_tamil':nf_tamil,
               'pcr':pcr,'raj':raj,
               'vpcr': vpcr
           }
    return render(request, 'homepage.html', context = data)





























    
   
   
     
    








