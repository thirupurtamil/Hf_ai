from django.shortcuts import render

def index(request):
    context = {
        "labels": [f"{i*50}/Call Option" if i % 2 == 0 else f"{i*50}/Put Option" for i in range(1, 15)],
        "values":  * 14,  # FIX: 14 zeros; * 14 என்பதற்கு பதில் list repetition
    }
    return render(request, "index.html", context)

