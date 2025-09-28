import math
from scipy.stats import norm

def black_scholes(S, K, T, r, sigma, option_type='call'):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    if option_type == 'call':
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

# Direct user input
spot = float(input("Spot Price (S): "))
strike = float(input("Strike Price (K): "))
days_to_expiry = int(input("Days to Expiry: "))
iv = float(input("Implied Volatility (IV in %): ")) / 100
r = float(input("Risk-free Rate (in %): ")) / 100
option_type = input("Option Type (call/put): ").lower()

T = days_to_expiry / 365

premium = black_scholes(spot, strike, T, r, iv, option_type)
print(f"\n{option_type.capitalize()} Option Premium: {premium:.2f}")