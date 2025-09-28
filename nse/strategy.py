# strategy.py
def determine_strategy(price_change, oi_change):
    """OI மற்றும் விலை மாற்றம் அடிப்படையில் ஸ்ட்ரேடஜியை கணக்கிடுதல்."""
    if price_change > 0 and oi_change > 0:
        return "⬆️LB"
    elif price_change < 0 and oi_change > 0:
        return "🔄SB"
    elif price_change > 0 and oi_change < 0:
        return "⬇️SC"
    elif price_change < 0 and oi_change < 0:
        return "⬇️🔴LWP"
    elif price_change > 0:
        return "🔄SCO"
    elif price_change < 0:
        return "🔄LWO"
    else:
        return "NIL"