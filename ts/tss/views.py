import math
from scipy.stats import norm
from django.shortcuts import render
import requests
import time
from datetime import datetime


    
    



def index(request):
    
    joke="Sastika_sri"
    r=datetime.now()

    return render(request,'index.html', context={'joke':joke,"r":r})


def black_scholes(S, K, T, r, sigma, option_type='call'):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def option(request):
    premium = None
    if request.method == 'POST':
        try:
            S = float(request.POST.get('spot'))
            K = float(request.POST.get('strike'))
            days = int(request.POST.get('days'))
            iv = float(request.POST.get('iv')) / 100
            r = float(request.POST.get('r')) / 100
            option_type = request.POST.get('option_type')

            T = days / 365
            premium = black_scholes(S, K, T, r, iv, option_type)
        except Exception as e:
            premium = f"Error: {e}"

    return render(request, 'option.html', {'premium': premium})
