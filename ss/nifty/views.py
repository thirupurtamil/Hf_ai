import requests 

from django.shortcuts import render 


import pandas as pd




data=[]

dsp=[]
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',}
with requests.session() as req:
    req.get('https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY',headers = headers)

    api_req=req.get('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY',headers = headers).json()
    for item in api_req['stocks']:
        data.append([
            
            item['metadata']['strikePrice'],
            item['metadata']['optionType'],
            
            ]),
        for item in api_req['stocks']:
             dsp.append([
            item['metadata']['strikePrice'],
            item['metadata']['optionType'],
            item['metadata']['openPrice'],
            
            ]),
            
            
        
        






cols=['STRIKEPRICE','OPTION']
df = pd.DataFrame(data, columns=cols)         
ds = df.head(14)          


dx= ds.pivot_table(index = ['OPTION'], aggfunc ='size') 



dss= df.head(6)
de= dss.pivot_table(index = ['OPTION'], aggfunc ='max') 
de1= dss.pivot_table(index = ['OPTION'], aggfunc ='min')


dz= df.head(14)

xc= dz.loc[dz['OPTION'] == 'Call'] 

xs=dz.loc[dz['OPTION'] == 'Put'] 




cols=['STRIKEPRICE','OPTION','OPEN']
dsp1 = pd.DataFrame(dsp, columns=cols)         
dsp2 = dsp1.head(14)         





def n50(request):
    tamil1 = dx[0]
    tamil = dx[1]
 
    t1 = de.max()
    t2 = de1.min()
    t1=t1[0]
    t2=t2[0]
    tt = t1-t2
    tt=tt
    
    data= dx
    la1= 8
    la2= 6
    la3= 22300
    la4= 22000
    la5= la3-la4
    
    r1=tamil-la1
    r2=tamil1-la2
    r3=t1-la3
    r4=t2-la4
    r5=la5-tt
    
    vs1=22000
    vs2= 'call'
    vs3=57
    vs4= 239
    vs5= 0000
    vs6=vs4-vs5
    vs7=vs1+vs3

    
    
    lvs1=22000
    lvs2= 'put'
    lvs3=130
    lvs4= 162
    lvs5= 0000
    lvs6=vs4-lvs5
    lvs7=lvs1-lvs3
    lvs8=lvs7-vs3
    vs8=vs7+lvs3    
    
   



    data = { 'tamil1':tamil1,'tamil':tamil,
             't1': t1,'t2':t2,'tt':tt,
           'la1':la1,'la2':la2,'la3':la3,'la4':la4,'la5':la5,
           'r1':r1,'r2':r2,'r3':r3,'r4':r4,'r5':r5,
           'vs1':vs1,'vs2':vs2,'vs3':vs3,'vs4':vs4,
            'vs5':vs5,'vs6':vs6,'vs7':vs7,'vs8':vs8,
              'lvs1':lvs1,'lvs2':lvs2,'lvs3':lvs3,'lvs4':lvs4,
            'lvs5':lvs5,'lvs6':lvs6,'lvs7':lvs7,'lvs8':lvs8,
            'xc':xc,'xs':xs,'data':data


            }

    return render(request, 'n50.html', context = data)
















    
   
   
     
    








