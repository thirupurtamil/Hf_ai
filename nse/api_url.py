

import requests
import pandas as pd
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry






# api_url.py
OPTION_CHAIN_URL = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
QUOTE_DERIVATIVE_URL = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'






# முதல் API-க்கான ஹெடர்கள்
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en,gu;q=0.9,hi;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY',
    'X-Requested-With': 'XMLHttpRequest'
}

# செஷன் துவக்குதல்
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

def initialize_session():
    try:
        session.get('https://www.nseindia.com', headers=headers, timeout=10)
        session.get('https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY', headers=headers, timeout=10)
    except Exception as e:
        print(f"செஷன் பிழை: {e}")

def fetch_option_data(expiry=None):
    u = f"{OPTION_CHAIN_URL}&expiryDate={expiry}" if expiry else OPTION_CHAIN_URL
    try:
        response = session.get(u, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API பிழை: {e}. தரவு கிடைக்கவில்லை.")
        return None

def fetch_quote_derivative_data():
    try:
        response = session.get(QUOTE_DERIVATIVE_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Quote Derivative API பிழை: {e}")
        return {'stocks': []}