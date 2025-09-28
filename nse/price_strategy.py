def price_strategy(open_price, yesterday_close, yesterday_high, yesterday_low):
    """
    ஓப்பன் ப்ரைஸ் மற்றும் முந்தைய நாள் விலைகளை அடிப்படையாகக் கொண்டு ஸ்ட்ரேடஜியை தீர்மானிக்கும் ஃபங்ஷன்.
    
    Args:
        open_price (float): இன்றைய ஓப்பன் ப்ரைஸ்
        yesterday_close (float): முந்தைய நாள் கிளோஸ் ப்ரைஸ்
        yesterday_high (float): முந்தைய நாள் உயர்ந்த ப்ரைஸ்
        yesterday_low (float): முந்தைய நாள் குறைந்த ப்ரைஸ்
        
    Returns:
        tuple: (சின்னம், வித்தியாசமான விலை அல்லது None)
    """
    price_diff = open_price - yesterday_close  # விலை வித்தியாசம்
    
    if open_price > yesterday_close and open_price > yesterday_high:
        return "🟢⬆️", price_diff
    elif open_price > yesterday_close:
        return " ✅🔼", price_diff
    elif open_price == yesterday_close:
        return "▶️↔️", None
    elif open_price < yesterday_low:
        return "🔴⬇️", price_diff
    else:
        return "🔵👉", None