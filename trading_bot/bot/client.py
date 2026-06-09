"""Low-level Binance Futures Testnet client.

Wraps raw REST calls with HMAC-SHA256 signing, timeout handling,
and structured logging of every request/response pair.
"""

from __future__ import annotations

import hashlib
import hmac
import time
import urllib.parse
from typing import Any

import requests

from .logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"
RECV_WINDOW = 5000  # ms

logger = setup_logger("trading_bot.client")


class BinanceClientError(Exception):
    """Raised for any Binance API-level error."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _sign(self, params: dict) -> dict:
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        signed: bool = False,
    ) -> Any:
        url = f"{BASE_URL}{endpoint}"
        params = params or {}

        if signed:
            params["timestamp"] = self._timestamp()
            params["recvWindow"] = RECV_WINDOW
            params = self._sign(params)

        logger.debug(
            "REQUEST  %s %s | params: %s",
            method.upper(),
            endpoint,
            {k: v for k, v in params.items() if k != "signature"},
        )

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, data=params, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            logger.debug(
                "RESPONSE %s %s | status=%s | body=%s",
                method.upper(),
                endpoint,
                response.status_code,
                response.text[:800],
            )

            data = response.json()

        except requests.exceptions.Timeout:
            logger.error("Request timed out: %s %s", method.upper(), url)
            raise
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error: %s", exc)
            raise
        except Exception as exc:
            logger.error("Unexpected error during request: %s", exc)
            raise

        # Binance returns error as {"code": <negative int>, "msg": "..."}
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceClientError(data["code"], data.get("msg", "Unknown error"))

        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_server_time(self) -> dict:
        """Ping the server and return its timestamp (useful for clock-sync check)."""
        return self._request("GET", "/fapi/v1/time")

    def get_exchange_info(self) -> dict:
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def get_account(self) -> dict:
        return self._request("GET", "/fapi/v2/account", signed=True)

    def new_order(self, **kwargs) -> dict:
        """Place a new futures order. kwargs map 1-to-1 to Binance API params."""
        return self._request("POST", "/fapi/v1/order", params=kwargs, signed=True)

    def get_order(self, symbol: str, order_id: int) -> dict:
        return self._request(
            "GET",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        return self._request(
            "DELETE",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )
