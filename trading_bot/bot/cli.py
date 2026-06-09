#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet Trading Bot.

Usage examples
--------------
# Market BUY
python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

# Limit SELL
python -m bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 100000

# Stop-Market BUY (bonus order type)
python -m bot.cli --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.01 --stop-price 95000

# Provide credentials inline (not recommended for production)
python -m bot.cli --api-key <KEY> --api-secret <SECRET> --symbol ETHUSDT --side BUY --type MARKET --quantity 0.1
"""

from __future__ import annotations

import argparse
import os
import sys

from .client import BinanceClient, BinanceClientError
from .logging_config import setup_logger
from .orders import format_order_response, place_order
from .validators import ValidationError

logger = setup_logger("trading_bot.cli")


# ──────────────────────────────────────────────
# Argument parser
# ──────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Credentials (fall back to env vars)
    creds = parser.add_argument_group("API credentials")
    creds.add_argument(
        "--api-key",
        default=os.getenv("BINANCE_TESTNET_API_KEY"),
        help="Binance Testnet API key (or set BINANCE_TESTNET_API_KEY env var)",
    )
    creds.add_argument(
        "--api-secret",
        default=os.getenv("BINANCE_TESTNET_API_SECRET"),
        help="Binance Testnet API secret (or set BINANCE_TESTNET_API_SECRET env var)",
    )

    # Order parameters
    order = parser.add_argument_group("Order parameters")
    order.add_argument("--symbol",     required=True,  help="Trading pair, e.g. BTCUSDT")
    order.add_argument("--side",       required=True,  choices=["BUY", "SELL"],              help="Order side")
    order.add_argument("--type",       required=True,  choices=["MARKET", "LIMIT", "STOP_MARKET"], dest="order_type", help="Order type")
    order.add_argument("--quantity",   required=True,  type=float, help="Quantity to trade")
    order.add_argument("--price",      default=None,   type=float, help="Limit price (required for LIMIT orders)")
    order.add_argument("--stop-price", default=None,   type=float, dest="stop_price", help="Stop price (required for STOP_MARKET orders)")
    order.add_argument("--tif",        default="GTC",  choices=["GTC", "IOC", "FOK"], help="Time-in-force for LIMIT orders (default: GTC)")

    return parser


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # ── Credential check ──
    if not args.api_key or not args.api_secret:
        parser.error(
            "API credentials are required.\n"
            "  Pass --api-key / --api-secret, or set env vars:\n"
            "  BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET"
        )

    # ── Print request summary ──
    print()
    print("─" * 52)
    print("  📤  ORDER REQUEST SUMMARY")
    print("─" * 52)
    print(f"  Symbol     : {args.symbol.upper()}")
    print(f"  Side       : {args.side.upper()}")
    print(f"  Type       : {args.order_type.upper()}")
    print(f"  Quantity   : {args.quantity}")
    if args.price:
        print(f"  Price      : {args.price}")
    if args.stop_price:
        print(f"  Stop Price : {args.stop_price}")
    print("─" * 52)
    print()

    try:
        client = BinanceClient(api_key=args.api_key, api_secret=args.api_secret)
        response = place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
            time_in_force=args.tif,
        )
        print(format_order_response(response))
        return 0

    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"\n  ❌  Validation Error: {exc}\n")
        return 1

    except BinanceClientError as exc:
        logger.error("Binance API error [%s]: %s", exc.code, exc.message)
        print(f"\n  ❌  Binance API Error ({exc.code}): {exc.message}\n")
        return 2

    except (ConnectionError, TimeoutError) as exc:
        logger.error("Network failure: %s", exc)
        print(f"\n  ❌  Network Error: {exc}\n")
        return 3

    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        print(f"\n  ❌  Unexpected Error: {exc}\n")
        return 99


if __name__ == "__main__":
    sys.exit(main())
