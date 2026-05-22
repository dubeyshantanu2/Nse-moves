"""
nse_client.py — Fetches top 5 gainers & losers directly from NSE India.
No calculations. NSE data is used as-is.
"""

import time
import logging
import requests

logger = logging.getLogger(__name__)

_NSE_BASE    = "https://www.nseindia.com"
_GAINERS_URL = f"{_NSE_BASE}/api/live-analysis-variations?index=gainers"
_LOSERS_URL  = f"{_NSE_BASE}/api/live-analysis-variations?index=loosers"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":           "application/json, text/plain, */*",
    "Accept-Language":  "en-US,en;q=0.9",
    "Accept-Encoding":  "gzip, deflate, br",
    "Referer":          "https://www.nseindia.com/",
    "X-Requested-With": "XMLHttpRequest",
}


def _make_session() -> requests.Session:
    """Warm up session to get NSE cookies."""
    s = requests.Session()
    s.headers.update(_HEADERS)
    s.get(_NSE_BASE, timeout=12)
    time.sleep(0.8)
    return s


def _top5(raw: dict) -> list[dict]:
    """
    NSE returns data grouped by index (NIFTY, BANKNIFTY, etc.).
    Pick the first group (usually NIFTY) and return top 5 as-is.
    """
    for stocks in raw.values():
        if isinstance(stocks, list) and stocks:
            return stocks[:5]
    return []


def get_top_movers() -> dict:
    session = _make_session()

    r_g = session.get(_GAINERS_URL, timeout=15)
    r_g.raise_for_status()

    r_l = session.get(_LOSERS_URL, timeout=15)
    r_l.raise_for_status()

    return {
        "gainers": _top5(r_g.json()),
        "losers":  _top5(r_l.json()),
    }
