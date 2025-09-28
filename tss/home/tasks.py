from celery import shared_task
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
from jugaad_data.nse import NSELive
from dateutil import parser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync




def retry_session(max_retries=3):
    session = requests.Session()
    retry = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}



@shared_task
def fur_list():
    session = retry_session()
    session.get("https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY", headers=headers)
    url = "https://www.nseindia.com/api/liveEquity-derivatives?index=nse50_fut"
    fut_data = session.get(url, headers=headers, cookies=dict(session.cookies)).json()

    # எல்லா expiry dates collect பண்ணும்
    expiry_dates = [item.get("expiryDate") for item in fut_data.get("data", []) if item.get("expiryDate")]
    if not expiry_dates:
        return []

    # nearest (current) expiry select பண்ணும்
    current_expiry = min(expiry_dates, key=lambda d: datetime.strptime(d, "%d-%b-%Y"))

    # current expiry items மட்டும் filter பண்ணி first 10 items
    data = []
    for item in fut_data.get("data", []):
        if item.get("expiryDate") == current_expiry:
            data.append({
                "expiry": item.get("expiryDate", "N/A"),
                "lastPrice": item.get("lastPrice", 0),
                "change": item.get("change", 0),
                "oi": item.get("openInterest", 0),
                "volume": item.get("totalTradedVolume", 0),
            })
            if len(data) >= 10:  # 10 items limit
                break
    return data




@shared_task
def opc_list():
    session = retry_session()
    session.get("https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY", headers=headers)
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    opt_data = session.get(url, headers=headers, cookies=dict(session.cookies)).json()

    records = opt_data.get("filtered", {}).get("data", [])
    data = []

    # underlying value fetch
    underlying = opt_data.get("records", {}).get("underlyingValue", 0)
    if not underlying:
        return []

    lower_strike = underlying - 9 * 50  # 10 strikes down
    upper_strike = underlying + 9 * 50  # 10 strikes up

    # expiry filter
    expiry_dates = [row.get("CE", {}).get("expiryDate") or row.get("PE", {}).get("expiryDate")
                    for row in records if row.get("CE") or row.get("PE")]
    if not expiry_dates:
        return []

    current_expiry = min(expiry_dates)

    for row in records:
        strike = row.get("strikePrice", 0)
        if lower_strike <= strike <= upper_strike:
            ce = row.get("CE") or {}
            pe = row.get("PE") or {}

            # filter current expiry
            ce_expiry = ce.get("expiryDate")
            pe_expiry = pe.get("expiryDate")
            if (ce_expiry == current_expiry) or (pe_expiry == current_expiry):
                data.append({
                    "Strike": strike,
                    "Call_OI": ce.get("openInterest", 0),
                    "Call_LTP": ce.get("lastPrice", 0),
                    "Put_OI": pe.get("openInterest", 0),
                    "Put_LTP": pe.get("lastPrice", 0),
                })
    return data

@shared_task
def acb_list():
    session = retry_session()
    session.get("https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY", headers=headers)
    url = "https://www.nseindia.com/api/quote-derivative?symbol=NIFTY"
    der_data = session.get(url, headers=headers, cookies=dict(session.cookies)).json()
    data = []
    for item in der_data.get("stocks", [])[:14]:
        m = item.get("metadata", {})
        data.append({
            "Strike": m.get("strikePrice", 0),
            "Option": m.get("optionType", "N/A"),
            "ltp": m.get("lastPrice", 0),
            "oi": item["marketDeptOrderBook"]["tradeInfo"]["openInterest"],
        })
    return data







@shared_task
def mkt_list():
    session = retry_session()
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    session.get("https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY", headers=headers)
    opt_data = session.get(url, headers=headers, cookies=dict(session.cookies)).json()

    timestamp = opt_data["records"]["timestamp"]

    # Safe parsing
    try:
        dt = datetime.strptime(timestamp, "%d-%b-%Y %H:%M:%S")
    except ValueError:
        dt = parser.parse(timestamp)  # auto parse any format

    hh, mm, weekday = dt.hour, dt.minute, dt.weekday()

    if weekday >= 5:
        status = "Closed (Weekend)"
    elif hh < 9 or (hh == 9 and mm < 15):
        status = "Pre-Open"
    elif (9 <= hh < 15) or (hh == 15 and mm <= 30):
        status = "Open"
    else:
        status = "Closed"

    return {"timestamp": dt.strftime("%Y-%m-%d %H:%M:%S IST"), "status": status}







@shared_task
def push_nifty_live():
    try:
        # NIFTY 50 live data fetch
        n = NSELive()
        nf = n.live_index('NIFTY 50')
        nf_lastprice = nf['data'][0]['lastPrice']
        nf_time = nf['timestamp']
        nf_open = nf['data'][0]['open']
        nf_pre_close = nf['data'][0]['previousClose']
        nf_dayhigh = nf['data'][0]['dayHigh']
        nf_daylow = nf['data'][0]['dayLow']

        nf_ver = round(nf_lastprice - nf_pre_close, 2)
        nf_ph = round(nf_dayhigh - nf_open, 2)
        nf_pl = round(nf_daylow - nf_open, 2)

        data = {
            "lastPrice": nf_lastprice,
            "timestamp": nf_time,
            "open": nf_open,
            "previousClose": nf_pre_close,
            "dayHigh": nf_dayhigh,
            "dayLow": nf_daylow,
            "change": nf_ver,
            "highDiff": nf_ph,
            "lowDiff": nf_pl
        }

        # Push via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "nifty_group",
            {"type": "nifty_update", "data": data}
        )

    except Exception as e:
        # Optional: push error to frontend
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "nifty_group",
            {"type": "nifty_update", "data": {"error": str(e)}}
        )