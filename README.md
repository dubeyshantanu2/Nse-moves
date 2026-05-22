# NSE Market Movers Discord Tracker

A lightweight, automated Python service that tracks the top 5 gainers and losers directly from the National Stock Exchange of India (NSE) and updates a single live dashboard message in a Discord channel via Webhooks.

Unlike standard bots, this script executes natively via Discord Webhooks, dropping the overhead of heavy websocket client frameworks while maintaining a clean, single-message status board that updates dynamically without flooding your channel.

---

## 🛠️ Features

* **[span_0](start_span)Live Dashboard Editing:** Posts a single message to your Discord channel and continuously patches (edits) it every cycle[span_0](end_span).
* **[span_1](start_span)Intelligent Auto-Recovery:** Automatically detects if the dashboard message was deleted on Discord and regenerates a fresh target layout seamlessly[span_1](end_span).
* **[span_2](start_span)Market-Hour Aware:** Native gatekeeping ensures API scrapers only fire between **9:15 AM and 3:30 PM IST on weekdays**, preserving resources and preventing rate limits when the exchange is closed[span_2](end_span).
* **[span_3](start_span)Fault Tolerant:** Implements a fallback system layout that routes API exceptions or network handshake timeouts directly into an error embed inside the channel, so you always know the service state[span_3](end_span).
* **[span_4](start_span)Daemon Deployment:** Pre-configured systemd unit ready to run securely in the background on your Linux server environment[span_4](end_span).

---

## 📁 Repository Structure

* [span_5](start_span)`bot.py` — The core application execution loop, timing logic, and Discord Webhook integration middleware[span_5](end_span).
* [span_6](start_span)`nse_client.py` — Custom network scraper that mimics browser handshakes to securely harvest session cookies and pull live-analysis arrays from NSE India[span_6](end_span).
* [span_7](start_span)`market-movers.service` — Systemd unit file structure to configure the script as a managed OS background daemon[span_7](end_span).
* [span_8](start_span)`requirements.txt` — Python dependencies needed for deployment[span_8](end_span).

---

## ⚙️ Configuration Setup

The service handles all sensitive credentials dynamically via environment variables. To configure it locally on your production server, create a secure environment file:

```bash
# Location: /root/market_movers/.env
DISCORD_WEBHOOK_URL=[https://discord.com/api/webhooks/your_webhook_id/your_webhook_token_here](https://discord.com/api/webhooks/your_webhook_id/your_webhook_token_here)
UPDATE_INTERVAL_SECONDS=300
