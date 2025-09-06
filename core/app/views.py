from django.shortcuts import render

def index(request):
    context = {
        "labels": [f"{i*50}/Call Option" if i % 2 == 0 else f"{i*50}/Put Option" for i in range(1, 15)],
        "values": [i*100 for i in range(1, 15)],  # or [50]*14
    }
    return render(request, "index.html", context)
