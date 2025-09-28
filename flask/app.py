import requests
import pandas as pd
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# முதல் API-க்கான ஹெடர்கள்
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en,gu;q=0.9,hi;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY',
    'X-Requested-With': 'XMLHttpRequest'
}

# API URLs
option_chain_url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
quote_derivative_url = 'https://www.nseindia.com/api/quote-derivative?symbol=NIFTY'

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
    u = f"{option_chain_url}&expiryDate={expiry}" if expiry else option_chain_url
    try:
        response = session.get(u, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API பிழை: {e}. தரவு கிடைக்கவில்லை.")
        return None

def fetch_quote_derivative_data():
    try:
        response = session.get(quote_derivative_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Quote Derivative API பிழை: {e}")
        return {'stocks': []}

def determine_strategy(price_change, oi_change):
    """OI மற்றும் விலை மாற்றம் அடிப்படையில் ஸ்ட்ரேடஜியை கணக்கிடுதல்."""
    if price_change > 0 and oi_change > 0:
        return "லாங் பில்ட்அப்"
    elif price_change < 0 and oi_change > 0:
        return "ஷார்ட் பில்ட்அப்"
    elif price_change > 0 and oi_change < 0:
        return "ஷார்ட் கவரிங்"
    elif price_change < 0 and oi_change < 0:
        return "லாங் அன்வைண்டிங்"
    elif price_change > 0:
        return "ஷார்ட் கவரிங் (OI மாற்றமில்லை)"
    elif price_change < 0:
        return "லாங் அன்வைண்டிங் (OI மாற்றமில்லை)"
    else:
        return "N/A"

def process_option_chain(opt_data, quote_data, underlying_value):
    if not opt_data or 'filtered' not in opt_data:
        print("ஆப்ஷன் தரவு கிடைக்கவில்லை அல்லது API பிழை.")
        return pd.DataFrame(), pd.DataFrame()

    # ஆப்ஷன் செயின் தரவு
    rawop = pd.DataFrame(opt_data['filtered']['data']).fillna(0)
    
    # Quote Derivative தரவை ஸ்ட்ரைக் விலை, ஆப்ஷன் வகை மற்றும் காலாவதி அடிப்படையில் ஒரு அகராதியாக மாற்றுதல்
    quote_dict = {}
    for item in quote_data.get('stocks', []):
        strike = item['metadata']['strikePrice']
        opt_type = item['metadata']['optionType']
        expiry = item['metadata']['expiryDate']
        key = (strike, opt_type, expiry)
        quote_dict[key] = {
            'open': item['metadata']['openPrice'],
            'high': item['metadata']['highPrice'],
            'low': item['metadata']['lowPrice'],
            'close': item['metadata']['lastPrice'],
            'prev_close': item['metadata'].get('prevClose', item['metadata']['openPrice']),
            'value': item['metadata']['totalTurnover']
        }

    # முழு தரவு அட்டவணையை உருவாக்குதல்
    full_data = []
    for _, row in rawop.iterrows():
        strike = int(row['strikePrice'])
        ce_data = row['CE'] if 'CE' in row and row['CE'] != 0 else {}
        pe_data = row['PE'] if 'PE' in row and row['PE'] != 0 else {}
        expiry = opt_data['records']['expiryDates'][0] if 'records' in opt_data else ''
        
        call_key = (strike, 'Call', expiry)
        put_key = (strike, 'Put', expiry)
        call_quote = quote_dict.get(call_key, {'open': 0, 'high': 0, 'low': 0, 'close': 0, 'prev_close': 0, 'value': 0})
        put_quote = quote_dict.get(put_key, {'open': 0, 'high': 0, 'low': 0, 'close': 0, 'prev_close': 0, 'value': 0})
        
        # கால் மற்றும் புட் விலை மாற்றம் கணக்கிடுதல்
        call_price_change = call_quote['close'] - call_quote['prev_close'] if call_quote['prev_close'] != 0 else \
                           call_quote['close'] - call_quote['open']
        put_price_change = put_quote['close'] - put_quote['prev_close'] if put_quote['prev_close'] != 0 else \
                          put_quote['close'] - put_quote['open']
        
        # கால் மற்றும் புட் ஸ்ட்ரேடஜி கணக்கிடுதல்
        call_strategy = determine_strategy(call_price_change, ce_data.get('changeinOpenInterest', 0))
        put_strategy = determine_strategy(put_price_change, pe_data.get('changeinOpenInterest', 0))
        
        full_data.append({
            'Call OI': int(ce_data.get('openInterest', 0)),
            'Call Change OI': int(ce_data.get('changeinOpenInterest', 0)),
            'Call Volume': int(ce_data.get('totalTradedVolume', 0)),
            'Call IV': round(ce_data.get('impliedVolatility', 0), 2),
            'Call Open': round(call_quote['open'], 2),
            'Call High': round(call_quote['high'], 2),
            'Call Low': round(call_quote['low'], 2),
            'Call Close': round(call_quote['close'], 2),
            'Call LTP': round(ce_data.get('lastPrice', 0), 2),
            'Call Value': round(call_quote['value'], 2),
            'Call Strategy': call_strategy,
            'Strike Price': strike,
            'Put OI': int(pe_data.get('openInterest', 0)),
            'Put Change OI': int(pe_data.get('changeinOpenInterest', 0)),
            'Put Volume': int(pe_data.get('totalTradedVolume', 0)),
            'Put IV': round(pe_data.get('impliedVolatility', 0), 2),
            'Put Open': round(put_quote['open'], 2),
            'Put High': round(put_quote['high'], 2),
            'Put Low': round(put_quote['low'], 2),
            'Put Close': round(put_quote['close'], 2),
            'Put LTP': round(pe_data.get('lastPrice', 0), 2),
            'Put Value': round(put_quote['value'], 2),
            'Put Strategy': put_strategy
        })

    full_df = pd.DataFrame(full_data)

    # ஸ்பாட் விலையைச் சுற்றி 31 வரிசைகளை வடிகட்டுதல்
    full_df['diff'] = abs(full_df['Strike Price'] - int(underlying_value))
    spot_price = full_df.loc[full_df['diff'].idxmin(), 'Strike Price']
    filtered_df = pd.concat([
        full_df[full_df['Strike Price'] < spot_price].sort_values(by='Strike Price', ascending=False).head(15),
        full_df[full_df['Strike Price'] == spot_price],
        full_df[full_df['Strike Price'] > spot_price].sort_values(by='Strike Price').head(15)
    ]).sort_values(by='Strike Price', ascending=False).drop(columns=['diff'])

    if len(filtered_df) != 31:
        print(f"எச்சரிக்கை: 31 வரிசைகள் எதிர்பார்க்கப்பட்டன, ஆனால் {len(filtered_df)} வரிசைகள் கிடைத்தன.")

    # உயர் வால்யூம் தரவு
    high_vol_data = []
    for _, row in filtered_df.iterrows():
        for t in ['Call', 'Put']:
            if row[f'{t} Volume'] != 0:
                # விலை மாற்றம் கணக்கிடுதல்: முதலில் LTP - prev_close, இல்லையென்றால் LTP - open, இல்லையென்றால் LTP - filtered_df.Close
                quote_key = (row['Strike Price'], t, opt_data['records']['expiryDates'][0])
                quote = quote_dict.get(quote_key, {'close': 0, 'prev_close': 0, 'open': 0})
                price_change = row[f'{t} LTP'] - quote['prev_close'] if quote['prev_close'] != 0 else \
                               row[f'{t} LTP'] - quote['open'] if quote['open'] != 0 else \
                               row[f'{t} LTP'] - row[f'{t} Close'] if row[f'{t} Close'] != 0 else 0
                oi_change = row[f'{t} Change OI']
                strategy = determine_strategy(price_change, oi_change)
                
                high_vol_data.append({
                    'Strike Price': int(row['Strike Price']),
                    'Type': t,
                    'Volume': int(row[f'{t} Volume']),
                    'OI': int(row[f'{t} OI']),
                    'Change OI': int(row[f'{t} Change OI']),
                    'LTP': round(row[f'{t} LTP'], 2),
                    'IV': round(row[f'{t} IV'], 2),
                    'Open': round(row[f'{t} Open'], 2),
                    'High': round(row[f'{t} High'], 2),
                    'Low': round(row[f'{t} Low'], 2),
                    'Close': round(row[f'{t} Close'], 2),
                    'Value': round(row[f'{t} Value'], 2),
                    'Strategy': strategy
                })
    high_vol_df = pd.DataFrame(high_vol_data).sort_values(by='Volume', ascending=False).head(20).reset_index(drop=True)
    high_vol_df['S.No'] = high_vol_df.index + 1
    high_vol_df = high_vol_df[['S.No', 'Strike Price', 'Type', 'Volume', 'OI', 'Change OI', 'LTP', 'IV', 'Open', 'High', 'Low', 'Close', 'Value', 'Strategy']]

    return filtered_df, high_vol_df

def check_ltp_similarity(filtered_df, opt_data):
    """கால் LTP மற்றும் புட் LTP ஒரே மதிப்பு அல்லது 1 புள்ளி வேறுபாடு உள்ள ஸ்ட்ரைக் விலைகளை சோதித்தல்."""
    if filtered_df.empty:
        return {"message": "வடிகட்டப்பட்ட தரவு காலியாக உள்ளது.", "matches": [], "closest": {}}

    timestamp = opt_data['records']['timestamp'] if opt_data and 'records' in opt_data else 'N/A'
    matches = []
    for _, row in filtered_df.iterrows():
        call_ltp = row['Call LTP']
        put_ltp = row['Put LTP']
        strike = row['Strike Price']
        if call_ltp != 0 and put_ltp != 0:
            ltp_diff = abs(call_ltp - put_ltp)
            if ltp_diff <= 1:
                total_ltp = round(call_ltp + put_ltp, 2)
                matches.append({
                    'Strike Price': int(strike),
                    'Time': timestamp.split(" ")[1] if " " in timestamp else timestamp,
                    'Call LTP': call_ltp,
                    'Put LTP': put_ltp,
                    'Total LTP': total_ltp,
                    'LTP Difference': ltp_diff
                })

    result = {"message": "", "matches": matches, "closest": {}}
    if not matches:
        result["message"] = "எந்த ஸ்ட்ரைக் விலையிலும் கால் மற்றும் புட் LTP ஒரே மதிப்பு அல்லது 1 புள்ளி வேறுபாடு இல்லை."
        valid_rows = filtered_df[(filtered_df['Call LTP'] != 0) & (filtered_df['Put LTP'] != 0)].copy()
        if not valid_rows.empty:
            valid_rows['LTP Difference'] = abs(valid_rows['Call LTP'] - valid_rows['Put LTP'])
            closest_row = valid_rows.loc[valid_rows['LTP Difference'].idxmin()]
            total_ltp = round(closest_row['Call LTP'] + closest_row['Put LTP'], 2)
            result["closest"] = {
                'Strike Price': int(closest_row['Strike Price']),
                'Time': timestamp.split(" ")[1] if " " in timestamp else timestamp,
                'Call LTP': closest_row['Call LTP'],
                'Put LTP': closest_row['Put LTP'],
                'Total LTP': total_ltp,
                'LTP Difference': closest_row['LTP Difference']
            }
        else:
            result["message"] += "\nமிகவும் நெருக்கமான LTP உள்ள ஸ்ட்ரைக் விலை இல்லை (எல்லா LTP மதிப்புகளும் 0)."
    
    return result

def analyze_max_oi_value_pair(filtered_df):
    """மிக உயர்ந்த OI உள்ள ஸ்ட்ரைக் விலையில் கால் மற்றும் புட் ஜோடியை அனாலிசிஸ் செய்து BEP கணக்கிடுதல்."""
    if filtered_df.empty:
        return {"message": "வடிகட்டப்பட்ட தரவு காலியாக உள்ளது.", "result": {}}

    filtered_df['Total OI'] = filtered_df['Call OI'] + filtered_df['Put OI']
    max_oi_row = filtered_df.loc[filtered_df['Total OI'].idxmax()]
    
    strike = int(max_oi_row['Strike Price'])
    call_close = round(max_oi_row['Call Close'], 2)
    put_close = round(max_oi_row['Put Close'], 2)
    call_value = round(max_oi_row['Call Value'], 2)
    put_value = round(max_oi_row['Put Value'], 2)
    
    bep1 = int(call_close + strike) if call_close != 0 else "N/A"
    bep2 = int(put_close - strike) if put_close != 0 else "N/A"
    bep3 = int((call_close + put_close) + strike) if call_close != 0 and put_close != 0 else "N/A"
    bep4 = int((call_close + put_close) - strike) if call_close != 0 and put_close != 0 else "N/A"
    
    result = {
        'ஸ்ட்ரைக் விலை': strike,
        'கால் க்ளோஸ்': call_close,
        'புட் க்ளோஸ்': put_close,
        'கால் மதிப்பு': call_value,
        'புட் மதிப்பு': put_value,
        'BEP1 (கால் க்ளோஸ் + ஸ்ட்ரைக்)': bep1,
        'BEP2 (புட் க்ளோஸ் - ஸ்ட்ரைக்)': bep2,
        'BEP3 (கால் + புட் க்ளோஸ் + ஸ்ட்ரைக்)': bep3,
        'BEP4 (கால் + புட் க்ளோஸ் - ஸ்ட்ரைக்)': bep4
    }
    
    return {"message": "", "result": result}

def analyze_max_value_pair(filtered_df):
    """மிக உயர்ந்த மதிப்பு (value) உள்ள ஸ்ட்ரைக் விலையில் கால் மற்றும் புட் ஜோடியை அனாலிசிஸ் செய்து BEP கணக்கிடுதல்."""
    if filtered_df.empty:
        return {"message": "வடிகட்டப்பட்ட தரவு காலியாக உள்ளது.", "result": {}}

    filtered_df['Total Value'] = filtered_df['Call Value'] + filtered_df['Put Value']
    max_value_row = filtered_df.loc[filtered_df['Total Value'].idxmax()]
    
    strike = int(max_value_row['Strike Price'])
    call_close = round(max_value_row['Call Close'], 2)
    put_close = round(max_value_row['Put Close'], 2)
    call_value = round(max_value_row['Call Value'], 2)
    put_value = round(max_value_row['Put Value'], 2)
    
    bep1 = int(call_close + strike) if call_close != 0 else "N/A"
    bep2 = int(put_close - strike) if put_close != 0 else "N/A"
    bep3 = int((call_close + put_close) + strike) if call_close != 0 and put_close != 0 else "N/A"
    bep4 = int((call_close + put_close) - strike) if call_close != 0 and put_close != 0 else "N/A"
    
    result = {
        'ஸ்ட்ரைக் விலை': strike,
        'கால் க்ளோஸ்': call_close,
        'புட் க்ளோஸ்': put_close,
        'கால் மதிப்பு': call_value,
        'புட் மதிப்பு': put_value,
        'BEP1 (கால் க்ளோஸ் + ஸ்ட்ரைக்)': bep1,
        'BEP2 (புட் க்ளோஸ் - ஸ்ட்ரைக்)': bep2,
        'BEP3 (கால் + புட் க்ளோஸ் + ஸ்ட்ரைக்)': bep3,
        'BEP4 (கால் + புட் க்ளோஸ் - ஸ்ட்ரைக்)': bep4
    }
    
    return {"message": "", "result": result}

def get_expiry_data():
    """காலாவதி தேதிகள் மற்றும் அடிப்படை மதிப்பைப் பெறுதல்."""
    initialize_session()
    opt_data = fetch_option_data()
    if not opt_data or 'records' not in opt_data:
        print("API காலாவதி தேதிகள் அல்லது அடிப்படை மதிப்பைப் பெற முடியவில்லை.")
        return None, None, 0, []

    expiry_dates = opt_data['records'].get('expiryDates', [])
    underlying_value = opt_data['records'].get('underlyingValue', 0)
    
    if not expiry_dates:
        return None, None, underlying_value, []

    current_date = datetime.now(pytz.timezone('Asia/Kolkata')).date()
    valid_expiries = sorted(
        [(exp_str, datetime.strptime(exp_str, '%d-%b-%Y').date()) for exp_str in expiry_dates
         if datetime.strptime(exp_str, '%d-%b-%Y').date() >= current_date],
        key=lambda x: x[1]
    )
    current_expiry_str = valid_expiries[0][0] if valid_expiries else None
    
    return current_expiry_str, None, underlying_value, expiry_dates

def importdata(opt_data):
    if not opt_data or 'filtered' not in opt_data:
        print("API பிழை: சுருக்கமான தரவைப் பெற முடியவில்லை.")
        return {"message": "API பிழை: சுருக்கமான தரவைப் பெற முடியவில்லை."}

    t_ce = int(opt_data['filtered']['CE']['totOI'])
    t_pe = int(opt_data['filtered']['PE']['totOI'])
    tc = int(opt_data['filtered']['CE']['totVol'])
    tp = int(opt_data['filtered']['PE']['totVol'])
    dt = opt_data['records']['timestamp']

    trend = int(t_pe - t_ce)
    tr = int(tp - tc)
    pcr_oi = round(t_pe / t_ce, 2) if t_ce != 0 else "N/A"
    pcr_vol = round(tp / tc, 2) if tc != 0 else "N/A"

    return {
        "நேரம்": dt.split(" ")[1],
        "கால் OI": t_ce,
        "புட் OI": t_pe,
        "கால் வால்யூம்": tc,
        "புட் வால்யூம்": tp,
        "வால்யூம் வேறுபாடு": tr,
        "போக்கு": trend,
        "PCR (OI)": pcr_oi,
        "PCR (வால்யூம்)": pcr_vol
    }

def analyze_high_volume(high_vol_df, selected_expiry):
    if high_vol_df.empty:
        return {"message": "நெட்வொர்க் பிழை.", "data": {}}

    grouped = high_vol_df.groupby('Strike Price')['Type'].apply(list)
    missing = [f"{strike} {t} காணவில்லை" for strike, types in grouped.items()
               for t in ['Call', 'Put'] if t not in types]
    
    call_count = int((high_vol_df['Type'] == 'Call').sum())
    put_count = int((high_vol_df['Type'] == 'Put').sum())
    
    pivot_df = high_vol_df.pivot(index='Strike Price', columns='Type', values=['OI', 'LTP', 'Value']).fillna(0)
    pivot_df['Total OI'] = pivot_df[('OI', 'Call')] + pivot_df[('OI', 'Put')]
    max_strike = int(pivot_df['Total OI'].idxmax())
    max_row = pivot_df.loc[max_strike]

    C = round(float(max_row[('LTP', 'Call')].item() if ('LTP', 'Call') in max_row else 0), 2)
    P = round(float(max_row[('LTP', 'Put')].item() if ('LTP', 'Put') in max_row else 0), 2)
    call_oi = int(max_row[('OI', 'Call')].item() if ('OI', 'Call') in max_row else 0)
    put_oi = int(max_row[('OI', 'Put')].item() if ('OI', 'Put') in max_row else 0)
    total_oi = int(max_row['Total OI'].item() if 'Total OI' in max_row else 0)
    call_value = round(float(max_row[('Value', 'Call')].item() if ('Value', 'Call') in max_row else 0), 2)
    put_value = round(float(max_row[('Value', 'Put')].item() if ('Value', 'Put') in max_row else 0), 2)

    pep1, pep2 = int(max_strike + C), int(max_strike - P)
    pep_up, pep_down = int(max_strike + (C + P)), int(max_strike - (C + P))

    top_6_rows = high_vol_df.head(6)
    call_strikes = top_6_rows[top_6_rows['Type'] == 'Call']['Strike Price']
    put_strikes = top_6_rows[top_6_rows['Type'] == 'Put']['Strike Price']
    range_up = int(call_strikes.max()) if not call_strikes.empty else "6 ஜோடி கால் இல்லை"
    range_down = int(put_strikes.min()) if not put_strikes.empty else "6 ஜோடி புட் இல்லை"
    RANGE = int(range_up - range_down) if isinstance(range_up, int) and isinstance(range_down, int) else "N/A"

    return {
        "message": "",
        "selected_expiry": selected_expiry,
        "missing_pairs": missing,
        "call_count": call_count,
        "put_count": put_count,
        "max_strike": max_strike,
        "call_oi": call_oi,
        "put_oi": put_oi,
        "total_oi": total_oi,
        "call_ltp": C,
        "put_ltp": P,
        "call_value": call_value,
        "put_value": put_value,
        "pep1": pep1,
        "pep2": pep2,
        "pep_up": pep_up,
        "pep_down": pep_down,
        "range_up": range_up,
        "range_down": range_down,
        "range": RANGE
    }

@app.route('/')
def index():
    with ThreadPoolExecutor(max_workers=3) as executor:
        expiry_future = executor.submit(get_expiry_data)
        current_expiry, _, underlying_value, expiry_dates = expiry_future.result()

        selected_expiry = current_expiry
        opt_future = executor.submit(partial(fetch_option_data, selected_expiry))
        quote_future = executor.submit(fetch_quote_derivative_data)
        opt_data = opt_future.result()
        quote_data = quote_future.result()
        
        filtered_df, high_vol_df = process_option_chain(opt_data, quote_data, underlying_value)
        
        # DataFrame-ஐ JSON ஆக மாற்றுதல்
        filtered_json = filtered_df.to_dict(orient='records') if not filtered_df.empty else []
        high_vol_json = high_vol_df.to_dict(orient='records') if not high_vol_df.empty else []
        
        ltp_similarity = check_ltp_similarity(filtered_df, opt_data)
        max_oi_pair = analyze_max_oi_value_pair(filtered_df)
        max_value_pair = analyze_max_value_pair(filtered_df)
        high_volume_analysis = analyze_high_volume(high_vol_df, selected_expiry)
        summary = importdata(opt_data)
        
        # Range Table-ஐ உருவாக்குதல்
        range_data = [{
            'Range Up': high_volume_analysis['range_up'],
            'Range Down': high_volume_analysis['range_down'],
            'Range': high_volume_analysis['range'],
            'Call Count': high_volume_analysis['call_count'],
            'Put Count': high_volume_analysis['put_count']
        }]
        
        # Missing Pairs Table-ஐ உருவாக்குதல்
        missing_data = [{'Missing Pair': pair} for pair in high_volume_analysis['missing_pairs']]
        
        return render_template('index.html',
                             filtered_data=filtered_json,
                             high_vol_data=high_vol_json,
                             ltp_similarity=ltp_similarity,
                             max_oi_pair=max_oi_pair,
                             max_value_pair=max_value_pair,
                             summary=summary,
                             nifty50=int(underlying_value) if underlying_value else 0,
                             selected_expiry=selected_expiry,
                             expiry_dates=expiry_dates,
                             range_data=range_data,
                             missing_data=missing_data)

@app.route('/api/option_chain')
def api_option_chain():
    with ThreadPoolExecutor(max_workers=3) as executor:
        expiry_future = executor.submit(get_expiry_data)
        current_expiry, _, underlying_value, expiry_dates = expiry_future.result()
        
        selected_expiry = current_expiry
        opt_future = executor.submit(partial(fetch_option_data, selected_expiry))
        quote_future = executor.submit(fetch_quote_derivative_data)
        opt_data = opt_future.result()
        quote_data = quote_future.result()
        
        filtered_df, high_vol_df = process_option_chain(opt_data, quote_data, underlying_value)
        
        high_volume_analysis = analyze_high_volume(high_vol_df, selected_expiry)
        range_data = [{
            'Range Up': high_volume_analysis['range_up'],
            'Range Down': high_volume_analysis['range_down'],
            'Range': high_volume_analysis['range'],
            'Call Count': high_volume_analysis['call_count'],
            'Put Count': high_volume_analysis['put_count']
        }]
        missing_data = [{'Missing Pair': pair} for pair in high_volume_analysis['missing_pairs']]
        
        return jsonify({
            'filtered_data': filtered_df.to_dict(orient='records') if not filtered_df.empty else [],
            'high_vol_data': high_vol_df.to_dict(orient='records') if not high_vol_df.empty else [],
            'ltp_similarity': check_ltp_similarity(filtered_df, opt_data),
            'max_oi_pair': analyze_max_oi_value_pair(filtered_df),
            'max_value_pair': analyze_max_value_pair(filtered_df),
            'summary': importdata(opt_data),
            'nifty50': int(underlying_value) if underlying_value else 0,
            'selected_expiry': selected_expiry,
            'expiry_dates': expiry_dates,
            'range_data': range_data,
            'missing_data': missing_data
        })

if __name__ == "__main__":
    app.run(debug=True)