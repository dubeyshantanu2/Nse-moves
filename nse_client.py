"""
nse_client.py — Fetches top 5 gainers & losers from Dhan.co.
Uses Next.js data extraction for reliable, structured data.
"""

import logging
import requests
import json
import re

logger = logging.getLogger(__name__)

_GAINERS_URL = "https://dhan.co/stock-market-live/top-gainers-today/"
_LOSERS_URL  = "https://dhan.co/stock-market-live/top-losers-today/"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

def _extract_from_dhan(url: str) -> list[dict]:
    """Extracts stock data from Dhan.co's Next.js data blob."""
    try:
        r = requests.get(url, headers=_HEADERS, timeout=15)
        r.raise_for_status()
        
        # Find the JSON blob in the HTML
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text)
        if not match:
            logger.error(f"Could not find __NEXT_DATA__ in {url}")
            return []
            
        data = json.loads(match.group(1))
        stocks = data.get('props', {}).get('pageProps', {}).get('listData', [])
        
        results = []
        for s in stocks[:5]:
            results.append({
                "symbol": s.get("Sym", "N/A"),
                "ltp": s.get("Ltp", 0.0),
                "netPrice": round(s.get("PPerchange", 0.0), 2),
                "change": round(s.get("Pchange", 0.0), 2)
            })
        return results
    except Exception as e:
        logger.error(f"Error scraping Dhan.co ({url}): {e}")
        return []

def get_top_movers() -> dict:
    logger.info("Fetching top movers from Dhan.co...")
    
    gainers = _extract_from_dhan(_GAINERS_URL)
    losers = _extract_from_dhan(_LOSERS_URL)
    
    return {
        "gainers": gainers,
        "losers": losers
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = get_top_movers()
    print(json.dumps(data, indent=2))
