# home/tasks.py (final copy)
import json
from celery import shared_task
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def fetch_nse_data(self):
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json, text/plain, */*",
    }

    try:
        s = requests.Session()
        s.get("https://www.nseindia.com", headers=headers, timeout=5)
        resp = s.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        underlying = data.get("records", {}).get("underlyingValue")
        rows = data.get("records", {}).get("data", [])
        ce_oi = None
        pe_oi = None
        if rows:
            first = rows[0]
            ce = first.get("CE")
            pe = first.get("PE")
            if ce:
                ce_oi = ce.get("openInterest")
            if pe:
                pe_oi = pe.get("openInterest")

        payload = {"nifty": underlying, "call_oi": ce_oi, "put_oi": pe_oi}

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "live_data_group",
            {"type": "live_data_message", "text": json.dumps(payload)},
        )

        return payload

    except requests.exceptions.RequestException as exc:
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            error_payload = {"error": f"Max retries exceeded: {str(exc)}"}
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "live_data_group",
                {"type": "live_data_message", "text": json.dumps(error_payload)},
            )
            return {"error": str(exc)}
    except Exception as exc:
        error_payload = {"error": str(exc)}
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "live_data_group",
            {"type": "live_data_message", "text": json.dumps(error_payload)},
        )
        return {"error": str(exc)}