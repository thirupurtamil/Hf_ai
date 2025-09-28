
from django.shortcuts import render

def home1(request):
    # minimal context; உனக்கு தேவையான data மேலே Celery மூலம் real-time வரும்
    context = {
        "title": "Live NSE Dashboard",
    }
    return render(request, "home1.html", context)
     
    



def dashboard(request):
    return render(request, "home/dashboard.html")
from django.http import JsonResponse
from .tasks import fur_list, opc_list, acb_list, mkt_list

def api_futures(request):
    data = fur_list.delay().get(timeout=30)
    return JsonResponse({"futures": data})

def api_options(request):
    data = opc_list.delay().get(timeout=30)
    return JsonResponse({"options": data})

def api_contracts(request):
    data = acb_list.delay().get(timeout=30)
    return JsonResponse({"contracts": data})

def api_market(request):
    data = mkt_list.delay().get(timeout=30)
    return JsonResponse({"market": data})


from django.http import JsonResponse
from jugaad_data.nse import NSELive

def nifty_fallback(request):
    try:
        n = NSELive()
        nf = n.live_index('NIFTY 50')
        return JsonResponse({
            "lastPrice": nf['data'][0]['lastPrice'],
            "timestamp": nf['timestamp'],
        })
    except Exception as e:
        return JsonResponse({"error": str(e)})





# Nifty Live Page
def nifty_view(request):
    return render(request, "home/nifty.html")

# Futures Table Page
def futures_view(request):
    return render(request, "home/futures.html")

# Options Table Page
def options_view(request):
    return render(request, "home/options.html")

# Active Contracts Page
def contracts_view(request):
    return render(request, "home/contracts.html")