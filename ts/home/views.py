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







def md():
   
   headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',}


   with requests.session() as req:
        req.get('https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY',headers = headers)

        api_req=req.get('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY',headers = headers).json()
  
   return api_req






def fu():
   
   headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',}


   with requests.session() as req:
        req.get('https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY',headers = headers)

        fu_req=req.get('https://www.nseindia.com/api/liveEquity-derivatives?index=nse50_fut',headers = headers).json()
  
   return fu_req













def dataframe():
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37','accept-encoding': 'gzip, deflate, br','accept-language': 'en-GB,en;q=0.9,en-US;q=0.8'}




    session = requests.Session()
    request = session.get(url,headers=headers)
    cookies = dict(request.cookies)
    response = session.get(url,headers=headers,cookies=cookies).json()
    rawdata = pd.DataFrame(response)
    rawop = pd.DataFrame(rawdata['filtered']['data']).fillna(0)
    data = []
    for i in range(0,len(rawop)):
        calloi = callcoi = cltp = putoi = putcoi = pltp = 0
        stp = rawop['strikePrice'][i]
        if(rawop['CE'][i]==0):
            calloi = callcoi = 0
        else:
            calloi = rawop['CE'][i]['openInterest']
            callcoi = rawop['CE'][i]['changeinOpenInterest']
            cltp = rawop['CE'][i]['lastPrice']
        if(rawop['PE'][i] == 0):
            putoi = putcoi = 0
        else:
            putoi = rawop['PE'][i]['openInterest']
            putcoi = rawop['PE'][i]['changeinOpenInterest']
            pltp = rawop['PE'][i]['lastPrice']
        opdata = {
            'CALL OI': calloi, 'CALL CHNG OI': callcoi, 'CALL LTP': cltp, 'STRIKE PRICE': stp,
            'PUT OI': putoi, 'PUT CHNG OI': putcoi, 'PUT LTP': pltp
        }
        
        data.append(opdata)
    optionchain = pd.DataFrame(data)
    return optionchain




def choi():
    data=[]


    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',}
    with requests.session() as req:
        req.get('https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY',headers = headers)

        api_req=req.get('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY',headers = headers).json()

        for item in api_req['stocks']:
            data.append([
            
            item['metadata']['strikePrice'],
            item['metadata']['optionType'],
            item['metadata']['openPrice'],
            item['metadata']["highPrice"],
            item['metadata']['lowPrice'],
            item['metadata']['lastPrice'],
            item['metadata']['numberOfContractsTraded'],
            item['metadata']['totalTurnover'],]),
            
        cols=['STRIKEPRICE','OPTION','OPEN',"HIGH",'LOW','LAST','VOL','VALUE']
        df = pd.DataFrame(data, columns=cols)         
        ds = df.head(14)
        dx = ds.pivot_table(index = ['OPTION'], aggfunc ='size') 
    

        dss = ds.filter(['STRIKEPRICE','OPTION',])
        dss = dss.head(14)
        de= dss.pivot_table(index = ['OPTION'], aggfunc ='max')
      
        de1= dss.pivot_table(index = ['OPTION'], aggfunc ='min')
     
        return data
    




def dataframe1():
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37','accept-encoding': 'gzip, deflate, br','accept-language': 'en-GB,en;q=0.9,en-US;q=0.8'}

    session = requests.Session()
    request = session.get(url,headers=headers)
    cookies = dict(request.cookies)






    response = session.get(url,headers=headers,cookies=cookies).json()
    rawdata = pd.DataFrame(response) 
    rawop = pd.DataFrame(rawdata['filtered']['data']).fillna(0)
    data = []
    for i in range(0,len(rawop)):
        calloi = callcoi = cltp = putoi = putcoi = pltp = 0
        stp = rawop['strikePrice'][i]
     
     
        if(rawop['CE'][i]==0):
            calloi = callcoi = 0
        else:
            calloi = rawop['CE'][i]['openInterest']
            callcoi = rawop['CE'][i]['changeinOpenInterest']
            cltp = rawop['CE'][i]['lastPrice']
            civ = rawop['CE'][i]['impliedVolatility']

        if(rawop['PE'][i] == 0):
            putoi = putcoi = 0
        else:
            putoi = rawop['PE'][i]['openInterest']
            putcoi = rawop['PE'][i]['changeinOpenInterest']
            pltp = rawop['PE'][i]['lastPrice']
            piv = rawop['PE'][i]['impliedVolatility']
            live = rawop['PE'][i]['underlyingValue']
    
        opdata = {
            'CALL OI': calloi, 'CALL CHNG OI': callcoi, 'CALL LTP': cltp,  'C-IV': civ,'STRIKE PRICE': stp,
           
            'PUT OI': putoi, 'PUT CHNG OI': putcoi, 'PUT LTP': pltp,'P-IV': piv,'LIV' : live,
        }
        
        data.append(opdata)
    optionchain1 = pd.DataFrame(data)
    return optionchain1










       










   
                 
     
 



            
        

def home1(request):
    
    

    acb = md()
    ss = acb["stocks"][0]
    ss = ss["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
    z = acb["stocks"][0]
    a1 = z["metadata"]["strikePrice"]
    aa1 = z["metadata"]["optionType"]
    d1 = z["metadata"]["numberOfContractsTraded"]
    v1  = z['metadata']['totalTurnover']
    op1 = z["marketDeptOrderBook"]["tradeInfo"]["openInterest"]

    y = acb["stocks"][1]
    a2 = y["metadata"]["strikePrice"]
    aa2 = y["metadata"]["optionType"]
    d2 = y["metadata"]["numberOfContractsTraded"]
    v2  = y['metadata']['totalTurnover']
    op2 = y["marketDeptOrderBook"]["tradeInfo"]["openInterest"]

    x = acb["stocks"][2]
    a3 = x["metadata"]["strikePrice"]
    aa3 = x["metadata"]["optionType"]
    d3 = x["metadata"]["numberOfContractsTraded"]
    v3  = x['metadata']['totalTurnover']
    op3 = x["marketDeptOrderBook"]["tradeInfo"]["openInterest"]


    w = acb["stocks"][3]
    a4 = w["metadata"]["strikePrice"]
    aa4 = w["metadata"]["optionType"]
    d4 = w["metadata"]["numberOfContractsTraded"]
    v4  = w['metadata']['totalTurnover']
    op4 = w["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
       

    v = acb["stocks"][4]
    a5 = v["metadata"]["strikePrice"]
    aa5 = v["metadata"]["optionType"]
    d5 = v["metadata"]["numberOfContractsTraded"]
    v5  = v['metadata']['totalTurnover']
    op5 = v["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
   
    u = acb["stocks"][5]
    a6 = u["metadata"]["strikePrice"]
    aa6 = u["metadata"]["optionType"]
    d6 = u["metadata"]["numberOfContractsTraded"]
    v6  = u['metadata']['totalTurnover'] 
    op6 = u["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
   
    t = acb["stocks"][6]
    a7 = t["metadata"]["strikePrice"]
    aa7 = t["metadata"]["optionType"]
    d7 = t["metadata"]["numberOfContractsTraded"]
    v7  = t['metadata']['totalTurnover'] 
    op7 = t["marketDeptOrderBook"]["tradeInfo"]["openInterest"]


    s = acb["stocks"][7]
    a8 = s["metadata"]["strikePrice"]
    aa8 = s["metadata"]["optionType"]
    d8 = s["metadata"]["numberOfContractsTraded"]
    v8  = s['metadata']['totalTurnover']
    op8 = s["marketDeptOrderBook"]["tradeInfo"]["openInterest"]

    r = acb["stocks"][8]
    a9 = r["metadata"]["strikePrice"]
    aa9 = r["metadata"]["optionType"]
    d9 = r["metadata"]["numberOfContractsTraded"]
    v9  = r['metadata']['totalTurnover']
    op9 = r["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
    
    q = acb["stocks"][9]
    a10 = q["metadata"]["strikePrice"]
    aa10 = q["metadata"]["optionType"]
    d10 = q["metadata"]["numberOfContractsTraded"]
    v10 = q['metadata']['totalTurnover']
    op10 = q["marketDeptOrderBook"]["tradeInfo"]["openInterest"]

    p = acb["stocks"][10]
    a11 = p["metadata"]["strikePrice"]
    aa11 = p["metadata"]["optionType"]
    d11 = p["metadata"]["numberOfContractsTraded"]
    v11  = p['metadata']['totalTurnover']
    op11 = p["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
   

    o = acb["stocks"][11]
    a12 = o["metadata"]["strikePrice"]
    aa12 = o["metadata"]["optionType"]
    d12 = o["metadata"]["numberOfContractsTraded"]
    v12  = o['metadata']['totalTurnover']
    op12 = o["marketDeptOrderBook"]["tradeInfo"]["openInterest"]

    l = acb["stocks"][12]
    a13 = l["metadata"]["strikePrice"]
    aa13 = l["metadata"]["optionType"]
    d13 = l["metadata"]["numberOfContractsTraded"]
    v13 = l['metadata']['totalTurnover'] 
    op13 = l["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
   

    m = acb["stocks"][13]
    a14 = m["metadata"]["strikePrice"]
    aa14 = m["metadata"]["optionType"]
    d14 = m["metadata"]["numberOfContractsTraded"]
    v14 = m['metadata']['totalTurnover'] 
    op14 = m["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
   
    dd2 = d1-d2
    dd3 = d2-d3
    dd4 = d3-d4
    dd5= d4-d5
    dd6= d5-d6
    dd7 =d6-d7

    dd8 = d7-d8
    dd9 = d8-d9
    dd10= d9-d10
    dd11= d10-d11
    dd12 = d11-d12
    dd13 = d12-d13
    dd14 = d13-d14

             
    ds = choi()
    cols=['STRIKEPRICE','OPTION','OPEN',"HIGH",'LOW','LAST','VOL','VALUE']
    df = pd.DataFrame(ds, columns=cols)         
    ds = df.head(14)
    dx = ds.pivot_table(index = ['OPTION'], aggfunc ='size') 
    

    dss = ds.filter(['STRIKEPRICE','OPTION',])
    dss = dss.head(6)
    de= dss.pivot_table(index = ['OPTION'], aggfunc ='max')
      
    de1= dss.pivot_table(index = ['OPTION'], aggfunc ='min')
     
    tamil = dx[0]
    
    
    tamil1 = dx[1]
 
    t1 = de.max()
    t1=t1[0]
    t2 = de1.min()
    t2=t2[0]
    tt = t1-t2
           


    





    
    












    aqq = acb["stocks"][0]
    aq1 = aqq["metadata"]["strikePrice"]
    aaq1 = aqq["metadata"]["optionType"]
    oq1 = aqq["metadata"]["openPrice"]
    hq1 = aqq["metadata"]["highPrice"]
    lq1 = aqq["metadata"]["lowPrice"]
    laq1 = aqq["metadata"]["lastPrice"]
    clq1 = aqq["metadata"]["closePrice"]
    dq1 = aqq["metadata"]["numberOfContractsTraded"]
    vq1  = aqq['metadata']['totalTurnover']

    aqq = acb["stocks"][1]
    aq2 = aqq["metadata"]["strikePrice"]
    aaq2 = aqq["metadata"]["optionType"]
    clq2 = aqq["metadata"]["closePrice"]
    oq2 = aqq["metadata"]["openPrice"]
    hq2 = aqq["metadata"]["highPrice"]
    lq2 = aqq["metadata"]["lowPrice"]
    laq2 = aqq["metadata"]["lastPrice"]
    dq2 = aqq["metadata"]["numberOfContractsTraded"]
    vq2  = aqq['metadata']['totalTurnover']



    aqq = acb["stocks"][2]
    aq3 = aqq["metadata"]["strikePrice"]
    aaq3 = aqq["metadata"]["optionType"]
    clq3 = aqq["metadata"]["closePrice"]
    oq3 = aqq["metadata"]["openPrice"]
    hq3 = aqq["metadata"]["highPrice"]
    lq3 = aqq["metadata"]["lowPrice"]
    laq3 = aqq["metadata"]["lastPrice"]
    dq3 = aqq["metadata"]["numberOfContractsTraded"]
    vq3  = aqq['metadata']['totalTurnover']



    aqq = acb["stocks"][3]
    aq4 = aqq["metadata"]["strikePrice"]
    aaq4 = aqq["metadata"]["optionType"]
    clq4 = aqq["metadata"]["closePrice"]
    oq4 = aqq["metadata"]["openPrice"]
    hq4 = aqq["metadata"]["highPrice"]
    lq4 = aqq["metadata"]["lowPrice"]
    laq4 = aqq["metadata"]["lastPrice"]
    dq4 = aqq["metadata"]["numberOfContractsTraded"]
    vq4  = aqq['metadata']['totalTurnover']


    aqq = acb["stocks"][4]
    aq5 = aqq["metadata"]["strikePrice"]
    aaq5 = aqq["metadata"]["optionType"]
    clq5 = aqq["metadata"]["closePrice"]
    oq5 = aqq["metadata"]["openPrice"]
    hq5 = aqq["metadata"]["highPrice"]
    lq5 = aqq["metadata"]["lowPrice"]
    laq5 = aqq["metadata"]["lastPrice"]
    dq5 = aqq["metadata"]["numberOfContractsTraded"]
    vq5 = aqq['metadata']['totalTurnover']




    aqq = acb["stocks"][5]
    aq6 = aqq["metadata"]["strikePrice"]
    aaq6 = aqq["metadata"]["optionType"]
    clq6 = aqq["metadata"]["closePrice"]
    oq6 = aqq["metadata"]["openPrice"]
    hq6 = aqq["metadata"]["highPrice"]
    lq6 = aqq["metadata"]["lowPrice"]
    laq6 = aqq["metadata"]["lastPrice"]
    dq6 = aqq["metadata"]["numberOfContractsTraded"]
    vq6 = aqq['metadata']['totalTurnover']





    aqq = acb["stocks"][6]
    aq7 = aqq["metadata"]["strikePrice"]
    aaq7 = aqq["metadata"]["optionType"]
    clq7 = aqq["metadata"]["closePrice"]
    oq7 = aqq["metadata"]["openPrice"]
    hq7 = aqq["metadata"]["highPrice"]
    lq7 = aqq["metadata"]["lowPrice"]
    laq7 = aqq["metadata"]["lastPrice"]
    dq7 = aqq["metadata"]["numberOfContractsTraded"]
    vq7 = aqq['metadata']['totalTurnover']



    aqq = acb["stocks"][7]
    aq8 = aqq["metadata"]["strikePrice"]
    aaq8 = aqq["metadata"]["optionType"]
    clq8 = aqq["metadata"]["closePrice"]
    oq8 = aqq["metadata"]["openPrice"]
    hq8 = aqq["metadata"]["highPrice"]
    lq8 = aqq["metadata"]["lowPrice"]
    laq8 = aqq["metadata"]["lastPrice"]
    dq8 = aqq["metadata"]["numberOfContractsTraded"]
    vq8 = aqq['metadata']['totalTurnover']





    aqq = acb["stocks"][8]
    aq9 = aqq["metadata"]["strikePrice"]
    aaq9 = aqq["metadata"]["optionType"]
    clq9 = aqq["metadata"]["closePrice"]
    oq9 = aqq["metadata"]["openPrice"]
    hq9 = aqq["metadata"]["highPrice"]
    lq9 = aqq["metadata"]["lowPrice"]
    laq9 = aqq["metadata"]["lastPrice"]
    dq9 = aqq["metadata"]["numberOfContractsTraded"]
    vq9 = aqq['metadata']['totalTurnover']

   


    aqq = acb["stocks"][9]
    aq10 = aqq["metadata"]["strikePrice"]
    aaq10 = aqq["metadata"]["optionType"]
    clq10 = aqq["metadata"]["closePrice"]
    oq10 = aqq["metadata"]["openPrice"]
    hq10 = aqq["metadata"]["highPrice"]
    lq10 = aqq["metadata"]["lowPrice"]
    laq10 = aqq["metadata"]["lastPrice"]
    dq10 = aqq["metadata"]["numberOfContractsTraded"]
    vq10 = aqq['metadata']['totalTurnover']



    
    aqq = acb["stocks"][10]
    aq11 = aqq["metadata"]["strikePrice"]
    aaq11 = aqq["metadata"]["optionType"]
    clq11 = aqq["metadata"]["closePrice"]
    oq11 = aqq["metadata"]["openPrice"]
    hq11 = aqq["metadata"]["highPrice"]
    lq11 = aqq["metadata"]["lowPrice"]
    laq11 = aqq["metadata"]["lastPrice"]
    dq11 = aqq["metadata"]["numberOfContractsTraded"]
    vq11 = aqq['metadata']['totalTurnover']


    aqq = acb["stocks"][11]
    aq12 = aqq["metadata"]["strikePrice"]
    aaq12 = aqq["metadata"]["optionType"]
    clq12 = aqq["metadata"]["closePrice"]
    oq12 = aqq["metadata"]["openPrice"]
    hq12 = aqq["metadata"]["highPrice"]
    lq12 = aqq["metadata"]["lowPrice"]
    laq12 = aqq["metadata"]["lastPrice"]
    dq12 = aqq["metadata"]["numberOfContractsTraded"]
    vq12  = aqq['metadata']['totalTurnover']



    aqq = acb["stocks"][12]
    aq13 = aqq["metadata"]["strikePrice"]
    aaq13 = aqq["metadata"]["optionType"]
    clq13 = aqq["metadata"]["closePrice"]
    oq13 = aqq["metadata"]["openPrice"]
    hq13 = aqq["metadata"]["highPrice"]
    lq13 = aqq["metadata"]["lowPrice"]
    laq13 = aqq["metadata"]["lastPrice"]
    dq13 = aqq["metadata"]["numberOfContractsTraded"]
    vq13 = aqq['metadata']['totalTurnover']


    aqq = acb["stocks"][13]
    aq14 = aqq["metadata"]["strikePrice"]
    aaq14 = aqq["metadata"]["optionType"]
    clq14 = aqq["metadata"]["closePrice"]
    oq14 = aqq["metadata"]["openPrice"]
    hq14 = aqq["metadata"]["highPrice"]
    lq14 = aqq["metadata"]["lowPrice"]
    laq14 = aqq["metadata"]["lastPrice"]
    dq14 = aqq["metadata"]["numberOfContractsTraded"]
    vq14  = aqq['metadata']['totalTurnover']



    n = NSELive()
    nf = n.live_index('NIFTY 50')
    nfpc = nf['data'][0]['previousClose']
    raj = acb["opt_timestamp"]
    n50 = acb["underlyingValue"]
    n56 = round(n50-nfpc,2)
   


    fut = fu()
    nfut = fut["data"][0]
    nft= nfut["lastPrice"]
    n55 =round(nft-n50,2)



    

    optionchain = dataframe()
    op = optionchain.head(90)
    opd = optionchain.set_index("STRIKE PRICE")
    oph = opd.iloc[-57:-9] 

    ops = oph.filter(["CALL OI"])
    opa = oph.filter(["PUT OI"])
    ops = ops.idxmax()
    ops = ops[0]
    opa = opa.idxmax()
    opa = opa[0]



    
    opss = oph.filter(["CALL CHNG OI"])
    ops1 = opss.idxmax()
    ops1 = ops1[0]
    opst = oph.filter(["PUT CHNG OI"])
    ops2 = opst.idxmax()
    ops2 = ops2[0]
  



    optionchain1 = dataframe1()
    op = optionchain1.head(90)


    opd1 = optionchain1.set_index("STRIKE PRICE")
    oph1 = opd1.iloc[-57:-10] 
    opc1 = oph1.filter((["CALL OI"]))
    opp1 = oph1.filter((["PUT OI"]))



    rs1 = dataframe1()

    rs1 = rs1.head(80)

    oph1=oph1.filter(['STRIKE PRICE','C-IV'])
    oph1=oph1.head(1)
    
    
    
    pre=1
    lpre=1
    hpre=1













    
    
    data = { 
               'a1':a1,'d1':d1,'v1':v1,'aa1':aa1,
               'a2':a2,'d2':dd2,'v2':v2,'aa2':aa2,
               'a3':a3,'d3':dd3,'v3':v3,'aa3':aa3,
               'a4':a4,'d4':dd4,'v4':v4,'aa4':aa4,
               'a5':a5,'d5':dd5,'v5':v5,'aa5':aa5,
               'a6':a6,'d6':dd6,'v6':v6,'aa6':aa6,

               'a7':a7,'d7':d7,'v7':v7,'aa7':aa7,
               'a8':a8,'d8':dd8,'v8':v8,'aa8':aa8,
               'a9':a9,'d9':dd9,'v9':v9,'aa9':aa9,

           'a10':a10,'d10':dd10,'v10':v10,'aa10':aa10,
           'a11':a11,'d11':dd11,'v11':v11,'aa11':aa11,
           'a12':a12,'d12':dd12,'v12':v12,'aa12':aa12,
            'a13':a13,'d13':d13,'v13':v13,'aa13':aa13,
            'a14':a14,'d14':dd14,'v14':v14,'aa14':aa14,
             










            'aq1':aq1,'aaq1':aaq1,'dq1':dq1,'vq1':vq1,'ivq1':clq1,
                'oq1':oq1,'hq1':hq1,'lq1':lq1,'laq1':laq1,
               
            'aq2':aq2,'aaq2':aaq2,'dq2':dq2,'vq2':vq2,'ivq2':clq2,
                'oq2':oq2,'hq2':hq2,'lq2':lq2,'laq2':laq2,

            'aq3':aq3,'aaq3':aaq3,'dq3':dq3,'vq3':vq3,'ivq3':clq3,
                'oq3':oq3,'hq3':hq3,'lq3':lq3,'laq3':laq3,

            'aq4':aq4,'aaq4':aaq4,'dq4':dq4,'vq4':vq4,'ivq4':clq4,
                'oq4':oq4,'hq4':hq4,'lq4':lq4,'laq4':laq4,


            'aq5':aq5,'aaq5':aaq5,'dq5':dq5,'vq5':vq5,'ivq5':clq5,
                'oq5':oq5,'hq5':hq5,'lq5':lq5,'laq5':laq5,

            'aq6':aq6,'aaq6':aaq6,'dq6':dq6,'vq6':vq6,'ivq6':clq6,
                'oq6':oq6,'hq6':hq6,'lq6':lq6,'laq6':laq6,
   
            'aq7':aq7,'aaq7':aaq7,'dq7':dq7,'vq7':vq7,'ivq7':clq7,
                'oq7':oq7,'hq7':hq7,'lq7':lq7,'laq7':laq7,

            'aq8':aq8,'aaq8':aaq8,'dq8':dq8,'vq8':vq8,'ivq8':clq8,
                'oq8':oq8,'hq8':hq8,'lq8':lq8,'laq8':laq8,


            'aq9':aq9,'aaq9':aaq9,'dq9':dq9,'vq9':vq9,'ivq9':clq9,
                'oq9':oq9,'hq9':hq9,'lq9':lq9,'laq9':laq9,


        'aq10':aq10,'aaq10':aaq10,'dq10':dq10,'vq10':vq10,'ivq10':clq10,            
               'oq10':oq10,'hq10':hq10,'lq10':lq10,'laq10':laq10,
        

         'aq11':aq11,'aaq11':aaq11,'dq11':dq11,'vq11':vq11,'ivq11':clq11,
                'oq11':oq11,'hq11':hq11,'lq11':lq11,'laq11':laq11,


         'aq12':aq12,'aaq12':aaq12,'dq12':dq12,'vq12':vq12,'ivq12':clq12,
                'oq12':oq12,'hq12':hq12,'lq12':lq12,'laq12':laq12,

         'aq13':aq13,'aaq13':aaq13,'dq13':dq13,'vq13':vq13,'ivq13':clq13,
                'oq13':oq13,'hq13':hq13,'lq13':lq13,'laq13':laq13,


          'aq14':aq14,'aaq14':aaq14,'dq14':dq14,'vq14':vq14,'ivq14':clq14,
                'oq14':oq14,'hq14':hq14,'lq14':lq14,'laq14':laq14,




        'raj':raj,'n50':n50, 'n55':n55,'n56':n56,'pre':pre,'hpre':hpre,
      'lpre':lpre,'nft': nft,'ops':ops,'opa':opa ,'ops1':ops1,'ops2':ops2,

           

        'tamil':tamil,'tamil1':tamil1,'oph1':oph1,'ss':ss,
             't1': t1,'t2':t2,'tt':tt,'opc1':opc1,'opp1':opp1,
      
        'op1':op1,'op2':op2,'op3':op3,'op4':op4,'op5':op5,'op6':op6,
        'op7':op7,'op8':op8,'op9':op9,'op10':op10,'op11':op11,'op12':op12,
        'op13':op13,'op14':op14,}







            
               
           
    return render(request, 'home1.html', context = data)














    
   
   
     
    







