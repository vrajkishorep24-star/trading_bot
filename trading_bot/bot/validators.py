"""Input validation helpers for order parameters."""

from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(ValueError):
    """Raised when user-supplied order parameters fail validation."""


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol.isalnum():
        raise ValidationError(
            f"Symbol '{symbol}' is invalid. Must be alphanumeric, e.g. BTCUSDT."
        )
    if len(symbol) < 5 or len(symbol) > 12:
        raise ValidationError(
            f"Symbol '{symbol}' length looks wrong. Expected something like BTCUSDT."
        )
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Side '{side}' is invalid. Choose from: {', '.join(VALID_SIDES)}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Order type '{order_type}' is invalid. Choose from: {', '.join(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity: str | float) -> float:
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity '{quantity}' is not a valid number.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than 0. Got: {qty}")
    return qty


def validate_price(price: str | float | None, order_type: str) -> float | None:
    if order_type in ("LIMIT", "STOP_MARKET"):
        if price is None:
            raise ValidationError(
                f"Price is required for {order_type} orders."
            )
        try:
            p = float(price)
        except (TypeError, ValueError):
            raise ValidationError(f"Price '{price}' is not a valid number.")
        if p <= 0:
            raise ValidationError(f"Price must be greater than 0. Got: {p}")
        return p
    return None  # MARKET orders don't need a price


def validate_stop_price(stop_price: str | float | None, order_type: str) -> float | None:
    if order_type == "STOP_MARKET":
        if stop_price is None:
            raise ValidationError("stopPrice is required for STOP_MARKET orders.")
        try:
            sp = float(stop_price)
        except (TypeError, ValueError):
            raise ValidationError(f"stopPrice '{stop_price}' is not a valid number.")
        if sp <= 0:
            raise ValidationError(f"stopPrice must be greater than 0. Got: {sp}")
        return sp
    return None
