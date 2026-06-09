"""Order placement logic — sits between the client layer and the CLI."""

from __future__ import annotations

from typing import Any

from .client import BinanceClient
from .logging_config import setup_logger
from .validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

logger = setup_logger("trading_bot.orders")


def _build_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    stop_price: float | None = None,
    time_in_force: str = "GTC",
) -> dict:
    params: dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }
    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = time_in_force
    if order_type == "STOP_MARKET":
        params["stopPrice"] = stop_price
    return params


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: str | float | None = None,
    stop_price: str | float | None = None,
    time_in_force: str = "GTC",
) -> dict:
    """
    Validate inputs, log a request summary, call the API, and return the response.
    Raises ValidationError for bad inputs, BinanceClientError for API-level failures.
    """
    # --- Validate ---
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    price = validate_price(price, order_type)
    stop_price = validate_stop_price(stop_price, order_type)

    # --- Log the request summary (also echoed to console via INFO handler) ---
    logger.info(
        "ORDER REQUEST | symbol=%s | side=%s | type=%s | qty=%s | price=%s | stopPrice=%s",
        symbol,
        side,
        order_type,
        quantity,
        price,
        stop_price,
    )

    params = _build_order_params(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
        time_in_force=time_in_force,
    )

    response = client.new_order(**params)

    logger.info(
        "ORDER RESPONSE | orderId=%s | status=%s | executedQty=%s | avgPrice=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
        response.get("avgPrice"),
    )

    return response


def format_order_response(response: dict) -> str:
    """Return a human-friendly summary string for CLI output."""
    lines = [
        "",
        "─" * 52,
        "  ✅  ORDER PLACED SUCCESSFULLY",
        "─" * 52,
        f"  Order ID   : {response.get('orderId', 'N/A')}",
        f"  Symbol     : {response.get('symbol', 'N/A')}",
        f"  Side       : {response.get('side', 'N/A')}",
        f"  Type       : {response.get('type', 'N/A')}",
        f"  Status     : {response.get('status', 'N/A')}",
        f"  Orig Qty   : {response.get('origQty', 'N/A')}",
        f"  Exec Qty   : {response.get('executedQty', 'N/A')}",
        f"  Avg Price  : {response.get('avgPrice', 'N/A')}",
        f"  Time       : {response.get('updateTime', 'N/A')}",
        "─" * 52,
        "",
    ]
    return "\n".join(lines)
