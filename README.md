# AI Milk Tea Bot - CASSO Entry Test 2026

Telegram chatbot for milk tea ordering, built for the CASSO Intern Software Engineer 2026 entry assignment.

## Overview

This project implements an AI-powered ordering assistant that:
- Recommends drinks from `Menu.csv`
- Supports natural-language ordering
- Supports guided ordering via inline buttons
- Creates QR payment links via payOS
- Verifies payment status and collects delivery info
- Outputs a preparation note for store staff

## Key Features

- **Guided ordering flow**: `/menu` -> category -> item -> size -> toppings
- **Natural-language flow**: parse order intent, quantity, size, and toppings
- **Cart management**: `/cart`, `/clear`
- **Checkout flow**: `/checkout` + payment confirmation + shipping information
- **Delivery information gate**: only accepts delivery details after payment is verified
- **Test mode (no real payment)** via `TEST_SKIP_PAYMENT=true`

## Tech Stack

- Python 3.10+
- `python-telegram-bot`
- LLM provider: Gemini or OpenAI
- payOS API for payment link + status checking
- Render for deployment (polling mode)

## Project Structure

- `bot.py`: Telegram handlers and conversation flow
- `config.py`: environment loading and validation
- `menu_service.py`: menu loading/search from CSV
- `llm_service.py`: recommendation and order parsing
- `order_service.py`: cart/order calculations and prep note
- `payos_service.py`: payOS integration
- `Menu.csv`: menu source data

## Prerequisites

- A Telegram bot token from BotFather
- One LLM API key:
  - Gemini: `GEMINI_API_KEY`
  - OpenAI: `OPENAI_API_KEY`
- payOS credentials (for real payment flow)

## Environment Variables

Create `.env` from `.env.example` and fill values:

- `TELEGRAM_BOT_TOKEN`
- `LLM_PROVIDER` (`gemini` or `openai`)
- `GEMINI_API_KEY`, `GEMINI_MODEL` (if using Gemini)
- `OPENAI_API_KEY`, `OPENAI_MODEL` (if using OpenAI)
- `STORE_NAME` (optional)
- `PAYOS_CLIENT_ID`
- `PAYOS_API_KEY`
- `PAYOS_CHECKSUM_KEY`
- `PAYOS_RETURN_URL`
- `PAYOS_CANCEL_URL`
- `TEST_SKIP_PAYMENT` (`false` for production, `true` for local testing)

## Local Setup

### Windows (PowerShell)

```powershell
cd c:\Me\bk\HK252\bot
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python bot.py
```

### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python bot.py
```

## Telegram Commands

- `/start`: welcome message and quick guide
- `/menu`: guided ordering with buttons
- `/cart`: current cart summary
- `/checkout`: create payment QR and continue checkout
- `/clear`: clear current cart

## Quick Test Scenarios

### Scenario A: Guided flow
1. `/start`
2. `/menu`
3. Pick item/size/toppings
4. `/cart`
5. `/checkout`
6. Tap `Toi da thanh toan`
7. Send: `Ten | So dien thoai | Dia chi`

### Scenario B: Natural-language flow
1. Send: `Dat 2 tra chanh leo size L them tran chau den`
2. `/cart`
3. `/checkout`

## Test Mode (No Real Payment)

Use this mode for local testing when you do not want to pay:

- Set `TEST_SKIP_PAYMENT=true`
- Bot sends a mock QR and bypasses payOS verification when tapping `Toi da thanh toan`
- Full delivery-info and prep-note flow can still be tested end-to-end

Important:
- Keep `TEST_SKIP_PAYMENT=false` on deployed/public environments

## Deployment (Render, Polling)

1. Push source code to GitHub
2. Create a Python Web Service on Render
3. Start command: `python bot.py`
4. Add all environment variables from `.env.example`
5. Deploy and verify bot responses on Telegram

## Keep-Alive on Free Tier

Render free instances may sleep on inactivity. To reduce cold starts:

1. Create a UptimeRobot HTTP monitor for your Render URL
2. Interval: every 5 minutes
3. This project already exposes an internal health server and supports `HEAD` requests

Note:
- Free tier cannot guarantee strict 24/7 uptime
- For best stability, paid plans are recommended

## Common Issues

- `Missing TELEGRAM_BOT_TOKEN`: `.env` missing token or wrong file name
- `Conflict: terminated by other getUpdates request`: same token running in multiple places (local + Render)
- No QR in local: payOS credentials missing; use `TEST_SKIP_PAYMENT=true` for mock checkout testing

## Submission Checklist (for HR)

- Source code repository link
- Demo video link
- Solution analysis PDF
- Telegram bot link (`https://t.me/<bot_username>`)
- Deployed bot URL (if provided)