from django.http.response import HttpResponse
from threading import Thread
from asgiref.sync import sync_to_async
from django.shortcuts import render 
import pandas as pd
import requests
from threading import *
import queue
import time 
import threading


start = time.time()








headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',}
with requests.session() as req:
    req.get('https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY',headers = headers)

    api_req=req.get('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY',headers = headers).json()
ak=api_req


datas=[]
def raj():
   
   
   for i in range(2):
       
       print([i])
       print(". live. :",api_req['underlyingValue'])
       print(". STR   :",api_req['stocks'][i]['metadata']['strikePrice'])
       
       print(". option:",api_req['stocks'][i]['metadata']['optionType'])
       print(". open  :",api_req['stocks'][i]['metadata']['openPrice'])
       print(". high  :",api_req['stocks'][i]['metadata']['highPrice'])
       print(". low   :",api_req['stocks'][i]['metadata']['lowPrice'])
       print(". last  :",api_req['stocks'][i]['metadata']['lastPrice'])
       print(". close :",api_req['stocks'][i]['metadata']['closePrice'])

       print(". vol   :",api_req['stocks'][i]['metadata']['numberOfContractsTraded'])
       print(". value :",api_req['stocks'][i]['metadata']['totalTurnover'])


       print(". oi    :",api_req['stocks'][i]['marketDeptOrderBook']['tradeInfo']['openInterest'])
       print(". coi   :",api_req['stocks'][i]['marketDeptOrderBook']['tradeInfo']['changeinOpenInterest'])
       print(". iv    :",api_req['stocks'][i]['marketDeptOrderBook']['otherInfo']['impliedVolatility'])
       
   return raj


def caj():
   
   
   for i in range(100):
       
       datas.append([
      
       api_req['stocks'][i]['metadata']['strikePrice'],
       api_req['stocks'][i]['metadata']['optionType'],
       api_req['stocks'][i]['metadata']['openPrice'],
       api_req['stocks'][i]['metadata']['highPrice'],
       api_req['stocks'][i]['metadata']['lowPrice'],
       api_req['stocks'][i]['metadata']['lastPrice'],
       api_req['stocks'][i]['metadata']['closePrice'],
       api_req['stocks'][i]['metadata']['numberOfContractsTraded'],
       api_req['stocks'][i]['metadata']['totalTurnover'],
       api_req['stocks'][i]['marketDeptOrderBook']['tradeInfo']['openInterest'],
       api_req['stocks'][i]['marketDeptOrderBook']['tradeInfo']['changeinOpenInterest'],
       
       api_req['stocks'][i]['marketDeptOrderBook']['otherInfo']['impliedVolatility'],])
       
   return caj



caj()
data1=[]
def stk():
   
   
   for i in range(20):
       
       data1.append(
      
       api_req['stocks'][i]['metadata']['strikePrice'],
       )
   return stk

stk()









def stockPicker(request):
    stock_picker = "0","1",2,3,4,5,6,7,8,9,10,
    print(stock_picker)
    return render(request, 'nifty50.html', {'stockpicker':stock_picker})


def stockTracker(request):
    
    stockpicker1 = request.GET['stockpicker']
    stockpicker2 = request.GET.getlist('stockpicker')
    s=int(stockpicker1)
    
    
    print("ttttttttttt",stockpicker1)
    data = {}
    
    
    n_threads = len(stockpicker2)
    thread_list = []
    que = queue.Queue()
    start = time.time()
   
    for i in range(14):
        thread = Thread(target = lambda q, arg1: q.put({s: arg1}), args = (que, ak['stocks'][s]['metadata']))
        thread_list.append(thread)
        thread_list[i].start()

    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)
    end = time.time()
    time_taken =  end - start
    print("processing_time:",round(time_taken,6))
            
    
    
    print(data)
    return render(request, 'stocktracker.html', {'data': data, 'room_name': 'track'})






    
   
   
     
    






