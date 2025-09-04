import os
from typing import Dict, Any
from agno.tools import tool
from dotenv import load_dotenv

# Load environment variables from .env (repository root)
load_dotenv()

try:
    import alpaca_trade_api as tradeapi
except Exception:
    tradeapi = None


@tool(show_result=True, stop_after_tool_call=True)
def place_order(symbol: str, qty: int, side: str = "buy", type: str = "market") -> Dict[str, Any]:
    """Place an order via Alpaca or simulate if Alpaca not configured."""
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET")
    base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

    if not api_key or not api_secret or tradeapi is None:
        return {
            "simulated": True,
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": type,
            "message": "Alpaca not configured; simulated order executed."
        }

    api = tradeapi.REST(api_key, api_secret, base_url=base_url, api_version='v2')
    try:
        order = api.submit_order(symbol=symbol, qty=qty, side=side, type=type, time_in_force='day')
        return {"order_id": order.id, "status": order.status, "simulated": False}
    except Exception as e:
        return {"error": str(e), "simulated": False}


@tool(show_result=True, stop_after_tool_call=True)
def get_account_overview() -> Dict[str, Any]:
    """Tool wrapper that delegates to internal helper."""
    return _get_account_overview_impl()


def _get_account_overview_impl() -> Dict[str, Any]:
    """Internal implementation for account overview (callable from other tools)."""
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET")
    base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")


    api = tradeapi.REST(api_key, api_secret, base_url=base_url, api_version='v2')
    try:
        acct = api.get_account()
        print(acct)
        return {
            "simulated": False,
            "cash": float(acct.cash),
            "buying_power": float(acct.buying_power),
            "equity": float(acct.equity),
            "status": acct.status,
        }
    except Exception as e:
        return {"error": str(e), "simulated": False}


@tool(show_result=True, stop_after_tool_call=True)
def get_positions() -> Dict[str, Any]:
    """Tool wrapper that delegates to internal helper."""
    return _get_positions_impl()


def _get_positions_impl() -> Dict[str, Any]:
    """Internal implementation returning current positions list (callable from other tools)."""
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET")
    base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

    if not api_key or not api_secret or tradeapi is None:
        # Simulated empty positions
        return {"simulated": True, "positions": []}

    api = tradeapi.REST(api_key, api_secret, base_url=base_url, api_version='v2')
    try:
        pos_list = api.list_positions()
        positions = []
        for p in pos_list:
            positions.append({
                "symbol": p.symbol,
                "qty": float(p.qty),
                "avg_entry_price": float(p.avg_entry_price),
                "market_value": float(p.market_value),
                "unrealized_pl": float(p.unrealized_pl),
            })
        return {"simulated": False, "positions": positions}
    except Exception as e:
        return {"error": str(e), "simulated": False}


@tool(show_result=True, stop_after_tool_call=True)
def get_portfolio_overview() -> Dict[str, Any]:
    """Return aggregated portfolio overview: total positions value + cash + summary."""
    # Call internal implementations to avoid invoking decorated tool objects
    acct = _get_account_overview_impl()
    positions_resp = _get_positions_impl()

    if "error" in acct:
        return acct
    if "error" in positions_resp:
        return positions_resp

    positions = positions_resp.get("positions", [])
    total_positions_value = sum(p.get("market_value", 0) for p in positions)
    cash = acct.get("cash", 0)
    equity = acct.get("equity", cash + total_positions_value)

    return {
        "simulated": acct.get("simulated", True),
        "cash": cash,
        "total_positions_value": total_positions_value,
        "equity": equity,
        "positions_count": len(positions),
        "positions": positions,
    }
