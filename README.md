# NSE Market Movers Discord Bot

A lightweight Python daemon that fetches top 5 gainers and losers from the NSE (National Stock Exchange of India) via Dhan.co and updates a single Discord message via Webhooks.

## Features
- **Clean Updates**: Updates the *same* Discord message every cycle instead of spamming the channel.
- **Reliable Data**: Uses a robust scraper for Dhan.co to bypass blocks common with the official NSE API.
- **Market Aware**: Only runs during IST market hours (9:15 AM - 3:30 PM).
- **Fly.io Ready**: Pre-configured for deployment as a background worker.

## Setup

1. **Environment Variables**:
   Create a `.env` file or set secrets in your hosting environment:
   - `DISCORD_WEBHOOK_URL`: Your Discord channel webhook URL.
   - `UPDATE_INTERVAL_SECONDS`: Frequency of updates (default: 300).

2. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Running Locally**:
   ```bash
   python bot.py
   ```

## Deployment (Fly.io)

This bot is configured to run as a background process on Fly.io.

```bash
fly deploy
```

## Data Source
Data is scraped from [Dhan.co](https://dhan.co/stock-market-live/top-gainers-today/) using their internal Next.js data structures for high reliability.
