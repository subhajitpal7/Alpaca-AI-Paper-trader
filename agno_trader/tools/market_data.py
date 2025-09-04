import json
import os
import time

import requests
from agno.tools import tool

_CACHE_FILE = os.path.join("tmp", "stock_price_cache.json")


def _read_cache() -> dict[str, dict]:
    try:
        with open(_CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_cache(cache: dict[str, dict]):
    try:
        os.makedirs(os.path.dirname(_CACHE_FILE), exist_ok=True)
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception:
        pass


def _alpha_vantage_quote(symbol: str, api_key: str) -> dict | None:
    try:
        url = (
            "https://www.alphavantage.co/query?function=GLOBAL_QUOTE"
            f"&symbol={symbol}&apikey={api_key}"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        quote = data.get("Global Quote") or {}
        price = quote.get("05. price")
        if price is not None:
            return {
                "symbol": symbol,
                "price": float(price),
                "time": None,
                "source": "alphavantage",
            }
    except Exception:
        return None


def get_stock_price_raw(
    symbol: str, max_retries: int = 3, backoff_base: float = 1.5
) -> dict:
    """
    Direct callable helper with the fetching logic (useful for unit tests and local
    calls).
    """
    # Use Alpha Vantage as the sole provider
    av_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not av_key:
        # If no API key, return cached value if available
        cache = _read_cache()
        cached = cache.get(symbol)
        if cached:
            return {
                "symbol": symbol,
                "price": cached.get("price"),
                "time": cached.get("time"),
                "source": "cache",
                "note": "no AV key, returning cached value",
            }
        return {"error": "Alpha Vantage API key not set (ALPHAVANTAGE_API_KEY)."}

    for attempt in range(1, max_retries + 1):
        av = _alpha_vantage_quote(symbol, av_key)
        if av:
            cache = _read_cache()
            cache[symbol] = {
                "price": av["price"],
                "time": av.get("time"),
                "source": "alphavantage",
            }
            _write_cache(cache)
            return av

        # if not successful, backoff and retry
        time.sleep(backoff_base**attempt)

    # Last resort: cached value
    cache = _read_cache()
    cached = cache.get(symbol)
    if cached:
        return {
            "symbol": symbol,
            "price": cached.get("price"),
            "time": cached.get("time"),
            "source": "cache",
            "note": "returning cached value after AV failures",
        }

    return {"error": "Failed to fetch price from Alpha Vantage after retries."}


@tool(show_result=True, stop_after_tool_call=True)
def get_stock_price(
    symbol: str, max_retries: int = 3, backoff_base: float = 1.5
) -> dict:
    """Agno tool wrapper that delegates to the raw helper."""
    return get_stock_price_raw(
        symbol, max_retries=max_retries, backoff_base=backoff_base
    )
