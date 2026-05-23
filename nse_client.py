"""
nse_client.py — Reliable NSE data via Yahoo Finance.
Used as a stable alternative since NSE India blocks cloud IPs.
"""

import logging
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)

# List of major NIFTY 50 / Large cap symbols to track
_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS",
    "INFY.NS", "SBIN.NS", "LICI.NS", "HINDUNILVR.NS", "ITC.NS",
    "LT.NS", "HCLTECH.NS", "BAJFINANCE.NS", "SUNPHARMA.NS", "ADANIENT.NS",
    "MARUTI.NS", "AXISBANK.NS", "ADANIPORTS.NS", "NTPC.NS",
    "KOTAKBANK.NS", "TITAN.NS", "ONGC.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS",
    "COALINDIA.NS", "BAJAJFINSV.NS", "JSWSTEEL.NS", "M&M.NS", "POWERGRID.NS",
    "ADANIPOWER.NS", "TATASTEEL.NS", "HINDALCO.NS", "GRASIM.NS", "NESTLEIND.NS"
]

def get_top_movers():
    logger.info(f"Fetching data for {len(_SYMBOLS)} symbols via Yahoo Finance...")
    
    try:
        # Fetch data in bulk
        data = yf.download(tickers=_SYMBOLS, period="1d", interval="1m", group_by='ticker', progress=False)
        
        movers = []
        for symbol in _SYMBOLS:
            try:
                # Get the last two points to calculate change
                ticker_data = data[symbol]
                if ticker_data.empty: continue
                
                last_price = ticker_data['Close'].iloc[-1]
                prev_close = ticker_data['Open'].iloc[0] # Using the day's start as reference
                
                change = last_price - prev_close
                p_change = (change / prev_close) * 100
                
                movers.append({
                    "symbol": symbol.replace(".NS", ""),
                    "ltp": round(last_price, 2),
                    "netPrice": round(p_change, 2),
                    "change": round(change, 2)
                })
            except Exception:
                continue

        # Sort by percentage change
        movers.sort(key=lambda x: x["netPrice"], reverse=True)
        
        gainers = [m for m in movers if m["netPrice"] > 0][:5]
        losers = [m for m in movers if m["netPrice"] < 0]
        losers.sort(key=lambda x: x["netPrice"]) # Most negative first
        losers = losers[:5]

        return {
            "gainers": gainers,
            "losers": losers
        }

    except Exception as e:
        logger.error(f"Yahoo Finance Fetch Error: {e}")
        return {"gainers": [], "losers": []}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = get_top_movers()
    import json
    print(json.dumps(res, indent=2))
