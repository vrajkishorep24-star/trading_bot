# trading_bot
# 🤖 Binance Futures Testnet Trading Bot

A clean, production-style Python CLI application for placing orders on the **Binance Futures Testnet (USDT-M)**.

---

## 📁 Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST client (signing, requests, error handling)
│   ├── orders.py          # Order placement logic + response formatter
│   ├── validators.py      # Input validation helpers
│   ├── logging_config.py  # Structured logger (file + console)
│   └── cli.py             # CLI entry point (argparse)
├── logs/
│   └── trading_bot_YYYYMMDD.log   # Auto-created on first run
├── README.md
└── requirements.txt
```

---

## ⚙️ Setup

### 1. Prerequisites

- Python 3.8+
- A [Binance Futures Testnet](https://testnet.binancefuture.com) account with API credentials

### 2. Clone & install dependencies

```bash
git clone https://github.com/<your-username>/trading-bot.git
cd trading_bot
pip install -r requirements.txt
```

### 3. Set your API credentials

**Option A — Environment variables (recommended)**

```bash
export BINANCE_TESTNET_API_KEY="your_api_key_here"
export BINANCE_TESTNET_API_SECRET="your_api_secret_here"
```

**Option B — Pass inline (for quick testing only)**

```bash
python -m bot.cli --api-key YOUR_KEY --api-secret YOUR_SECRET ...
```

---

## 🚀 How to Run

### Place a MARKET BUY order

```bash
python -m bot.cli \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.01
```

### Place a LIMIT SELL order

```bash
python -m bot.cli \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.01 \
  --price 72000
```

### Place a STOP_MARKET BUY order *(bonus)*

```bash
python -m bot.cli \
  --symbol BTCUSDT \
  --side BUY \
  --type STOP_MARKET \
  --quantity 0.01 \
  --stop-price 65000
```

### Full flag reference

```
--symbol       Trading pair, e.g. BTCUSDT (required)
--side         BUY or SELL (required)
--type         MARKET | LIMIT | STOP_MARKET (required)
--quantity     Float quantity to trade (required)
--price        Limit price — required for LIMIT orders
--stop-price   Stop trigger price — required for STOP_MARKET orders
--tif          Time-in-force for LIMIT: GTC | IOC | FOK (default: GTC)
--api-key      Override env var BINANCE_TESTNET_API_KEY
--api-secret   Override env var BINANCE_TESTNET_API_SECRET
```

---

## 📋 Sample Output

```
────────────────────────────────────────────────────
  📤  ORDER REQUEST SUMMARY
────────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.01
────────────────────────────────────────────────────

2025-06-01 14:22:01 | INFO | ORDER REQUEST | symbol=BTCUSDT | side=BUY | type=MARKET ...

────────────────────────────────────────────────────
  ✅  ORDER PLACED SUCCESSFULLY
────────────────────────────────────────────────────
  Order ID   : 4458196
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Status     : FILLED
  Orig Qty   : 0.01
  Exec Qty   : 0.01
  Avg Price  : 67341.20
  Time       : 1748783522014
────────────────────────────────────────────────────
```

---

## 📝 Logging

Logs are written to `logs/trading_bot_YYYYMMDD.log` and include:

- **DEBUG**: full request params (excluding signature) and raw API response body
- **INFO**: order request & response summaries, app lifecycle events
- **WARNING / ERROR**: validation failures and API errors with codes

Sample log files from real testnet runs are included in `logs/`.

---

## 🏗️ Design Decisions & Assumptions

| Decision | Reason |
|---|---|
| Raw `requests` over `python-binance` | Fewer dependencies, full transparency over signing and HTTP |
| Separate `client.py` / `orders.py` / `validators.py` | Clean separation of concerns; easy to extend or test |
| Env vars for credentials | Avoids accidental credential commits |
| `logging` module (not `print`) | Structured, filterable, goes to file and console |
| `STOP_MARKET` as bonus type | Simpler than OCO but genuinely useful in futures trading |
| Validation before API call | Fails fast, saves API quota, gives friendlier error messages |

---

## 🧪 Running Validation Tests

```bash
# Should print a validation error (no price for LIMIT)
python -m bot.cli --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01

# Should print a validation error (invalid side)
python -m bot.cli --symbol BTCUSDT --side LONG --type MARKET --quantity 0.01
```

---

## 📦 Dependencies

```
requests>=2.31.0
```

No other third-party dependencies — just Python's standard library + `requests`.
