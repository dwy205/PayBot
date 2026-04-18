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


## Project Structure

- `bot.py`: Telegram handlers and conversation flow
- `config.py`: environment loading and validation
- `menu_service.py`: menu loading/search from CSV
- `llm_service.py`: recommendation and order parsing
- `order_service.py`: cart/order calculations and prep note
- `payos_service.py`: payOS integration
- `Menu.csv`: menu source data


## Local Setup

### Windows (PowerShell)

```powershell
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

- Telegram bot link (`https://t.me/paychatcassobot`)
