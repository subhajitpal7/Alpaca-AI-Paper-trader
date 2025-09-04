import os
from typing import Any

from agno.tools import tool
from dotenv import load_dotenv

# Load environment variables from .env (repository root)
load_dotenv()

try:
    import alpaca_trade_api as tradeapi
except Exception:
    tradeapi = None


@tool(show_result=True, stop_after_tool_call=True)
def place_order(
    symbol: str, qty: int, side: str = "buy", type: str = "market"
) -> dict[str, Any]:
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
            "message": "Alpaca not configured; simulated order executed.",
        }

    api = tradeapi.REST(api_key, api_secret, base_url=base_url, api_version="v2")
    try:
        order = api.submit_order(
            symbol=symbol, qty=qty, side=side, type=type, time_in_force="day"
        )
        return {"order_id": order.id, "status": order.status, "simulated": False}
    except Exception as e:
        return {"error": str(e), "simulated": False}


@tool(show_result=True, stop_after_tool_call=True)
def get_account_overview() -> dict[str, Any]:
    """Tool wrapper that delegates to internal helper."""
    return _get_account_overview_impl()


def _get_account_overview_impl() -> dict[str, Any]:
    """Internal implementation for account overview (callable from other tools)."""
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET")
    base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    print(api_key, api_secret, base_url)
    # if not api_key or not api_secret or tradeapi is None:
    #     return {
    #         "simulated": True,
    #         "cash": 100000,  # Simulated cash
    #         "buying_power": 100000,  # Simulated buying power
    #         "equity": 100000,  # Simulated equity
    #         "status": "ACTIVE",
    #         "message": "Alpaca not configured; returning simulated account overview."
    #     }

    api = tradeapi.REST(
        key_id=api_key, secret_key=api_secret, base_url=base_url, api_version="v2"
    )
    try:
        acct = api.get_account()
        print(acct)
        return {
            "simulated": False,
            "cash": float(acct.cash),
            "buying_power": float(acct.buying_power),
            "equity": float(acct.equity),
            "portfolio_value": float(acct.portfolio_value),
            "status": acct.status,
        }
    except Exception as e:
        return {"error": str(e), "simulated": False}


@tool(show_result=True, stop_after_tool_call=True)
def get_positions() -> dict[str, Any]:
    """Tool wrapper that delegates to internal helper."""
    return _get_positions_impl()


def _get_positions_impl() -> dict[str, Any]:
    """
    Internal implementation returning current positions list (callable from other
    tools).
    """
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET")
    base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

    if not api_key or not api_secret or tradeapi is None:
        # Simulated empty positions
        return {"simulated": True, "positions": []}

    api = tradeapi.REST(api_key, api_secret, base_url=base_url, api_version="v2")
    try:
        pos_list = api.list_positions()
        positions = []
        for p in pos_list:
            positions.append(
                {
                    "symbol": p.symbol,
                    "qty": float(p.qty),
                    "avg_entry_price": float(p.avg_entry_price),
                    "market_value": float(p.market_value),
                    "unrealized_pl": float(p.unrealized_pl),
                }
            )
        return {"simulated": False, "positions": positions}
    except Exception as e:
        return {"error": str(e), "simulated": False}


@tool(show_result=True, stop_after_tool_call=True)
def get_portfolio_overview() -> dict[str, Any]:
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
    portfolio_value = acct.get("portfolio_value", equity)

    print("\n--- Portfolio Summary ---")
    print(f"Portfolio Value: ${portfolio_value:,.2f}")
    print(f"Cash: ${cash:,.2f}")
    print(f"Total Positions Value: ${total_positions_value:,.2f}")
    print(f"Number of Positions: {len(positions)}")
    print("-------------------------\n")

    return {
        "simulated": acct.get("simulated", True),
        "cash": cash,
        "total_positions_value": total_positions_value,
        "equity": equity,
        "portfolio_value": portfolio_value,
        "positions_count": len(positions),
        "positions": positions,
    }
