"""
bot.py — Market Movers Webhook
Only runs between 9:15 AM and 3:30 PM IST on weekdays.
Updates a single message via Discord Webhook.
"""

import os
import asyncio
import logging
from datetime import datetime, timezone, time
from zoneinfo import ZoneInfo
import requests
from dotenv import load_dotenv

load_dotenv()

from aiohttp import web
from nse_client import get_top_movers

# Configurations
WEBHOOK_URL     = os.getenv("DISCORD_WEBHOOK_URL", "")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL_SECONDS", "300"))

IST = ZoneInfo("Asia/Kolkata")
MARKET_OPEN  = time(9, 15)
MARKET_CLOSE = time(15, 30)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Tracks the message ID across cycles to update the same layout instead of spamming
_message_id: str | None = None

# Global state for web dashboard
_latest_data = {"gainers": [], "losers": [], "last_updated": None}

async def handle_index(request):
    return web.FileResponse(os.path.join(os.path.dirname(__file__), 'index.html'))

async def handle_data(request):
    return web.json_response(_latest_data)

async def start_web_server():
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index),
        web.get('/api/data', handle_data)
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", "8080"))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Web dashboard started on http://0.0.0.0:{port}")



def is_market_open() -> bool:
    now = datetime.now(IST)
    # Skip weekends
    if now.weekday() >= 5:
        return False
    return MARKET_OPEN <= now.time() <= MARKET_CLOSE


def build_embed_payload(data: dict) -> dict:
    embed = {
        "title": "📊  NSE Market Movers — Today",
        "color": 1733608,  # Hex 0x1a73e8 converted to decimal integers for Webhook JSON payload
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {
            "text": f"Auto-refreshes every {UPDATE_INTERVAL // 60}m  •  Source: Dhan.co"
        },
        "fields": []
    }

    gainers = data.get("gainers", [])
    if gainers:
        lines = []
        for i, s in enumerate(gainers, 1):
            lines.append(
                f"`{i}.` **{s['symbol']}** "
                f"₹{s['ltp']}  "
                f"🟢 +{s['netPrice']}%  (₹+{s['change']})"
            )
        embed["fields"].append({"name": "🚀 Top Gainers", "value": "\n".join(lines), "inline": False})

    losers = data.get("losers", [])
    if losers:
        lines = []
        for i, s in enumerate(losers, 1):
            lines.append(
                f"`{i}.` **{s['symbol']}** "
                f"₹{s['ltp']}  "
                f"🔴 {s['netPrice']}%  (₹{s['change']})"
            )
        embed["fields"].append({"name": "📉 Top Losers", "value": "\n".join(lines), "inline": False})

    return {"embeds": [embed]}


def build_error_payload(error: str) -> dict:
    return {
        "embeds": [{
            "title": "⚠️  Market Movers — Fetch Error",
            "description": f"```{error}```",
            "color": 16729156,  # Hex 0xff4444 converted to decimal
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "footer": {"text": "Will retry on next cycle"}
        }]
    }


def send_or_edit_webhook(payload: dict) -> None:
    global _message_id
    
    # Appending ?wait=true forces Discord to return the full message JSON back, including its internal ID
    url = f"{WEBHOOK_URL}?wait=true"
    
    try:
        if _message_id is None:
            # First execution or message got deleted: POST a new message
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            _message_id = response.json().get("id")
            logger.info(f"Posted fresh webhook message: {_message_id}")
        else:
            # Subsequent updates: PATCH the specific unique message ID
            edit_url = f"{WEBHOOK_URL}/messages/{_message_id}"
            response = requests.patch(edit_url, json=payload, timeout=10)
            
            # Safe recovery mechanism if someone manual deletes the bot message on Discord
            if response.status_code == 404:
                logger.warning("Previous message was deleted or missing. Rebuilding target message...")
                _message_id = None
                send_or_edit_webhook(payload)
            else:
                response.raise_for_status()
                logger.info(f"Successfully updated webhook message: {_message_id}")
                
    except Exception as e:
        logger.error(f"Failed to push update to Discord Webhook: {e}")


async def main_loop():
    logger.info("Market Movers Webhook Daemon Service Running.")
    
    # Start Web Server
    await start_web_server()
    
    # Force one update on startup so the user sees data immediately (even if market is closed)
    logger.info("Performing startup fetch...")
    try:
        data = await asyncio.to_thread(get_top_movers)
        
        # Update Web Dashboard Data
        _latest_data["gainers"] = data.get("gainers", [])
        _latest_data["losers"] = data.get("losers", [])
        _latest_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        payload = build_embed_payload(data)
        if not is_market_open():
            payload["embeds"][0]["title"] = "📊  NSE Market Movers — (Last Session)"
        send_or_edit_webhook(payload)
    except Exception as e:
        logger.error(f"Startup fetch failed: {e}")

    while True:
        if not is_market_open():
            logger.info("Market closed — skipping periodic update.")
        else:
            try:
                # Offload synchronous requests process to an async-safe thread pool worker
                data = await asyncio.to_thread(get_top_movers)
                
                # Update Web Dashboard Data
                _latest_data["gainers"] = data.get("gainers", [])
                _latest_data["losers"] = data.get("losers", [])
                _latest_data["last_updated"] = datetime.now(timezone.utc).isoformat()
                
                payload = build_embed_payload(data)
            except Exception as e:
                logger.error(f"Fetch failed: {e}")
                payload = build_error_payload(str(e))
            
            send_or_edit_webhook(payload)
            
        await asyncio.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    if not WEBHOOK_URL:
        raise SystemExit("❌  DISCORD_WEBHOOK_URL environment variable is missing.")
    
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logger.info("Exiting on manual signal interrupt.")
