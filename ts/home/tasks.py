from celery import shared_task
import requests
import pandas as pd
import redis
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Redis connection
redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0)

@shared_task
def fetch_nse_data():
    data = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    }

    with requests.Session() as req:
        req.get('https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY', headers=headers)
        api_req = req.get('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY', headers=headers).json()
        
        for item in api_req['stocks']:
            data.append([
                item['metadata']['strikePrice'],
                item['metadata']['optionType'],
                item['metadata']['openPrice'],
                item['metadata']["highPrice"],
                item['metadata']['lowPrice'],
                item['metadata']['lastPrice'],
                item['metadata']['numberOfContractsTraded'],
                item['metadata']['totalTurnover'],
                item['marketDeptOrderBook']['tradeInfo']['changeinOpenInterest'],
                item['marketDeptOrderBook']['tradeInfo']['openInterest'],
                item['underlyingValue'],
                item['metadata']['expiryDate'],
                item['marketDeptOrderBook']['otherInfo']['impliedVolatility']
            ])

    df = pd.DataFrame(
        data,
        columns=[
            'Strike', 'Option', 'open', 'high', 'low', 'ltp',
            'volume', 'value', 'change', 'open_in',
            'n50', 'expriydate', 'iv'
        ]
    )

    print(df.head(1))
    result = df.to_dict(orient="records")

    # Save Redis
    redis_client.set("nse:data", str(result))

    # Push via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "live_data",
        {
            "type": "send.live.data",
            "message": result,
        }
    )

    return result