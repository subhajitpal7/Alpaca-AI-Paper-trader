from agno.agent import Agent
from agno.models.google import Gemini
from agno.team import Team

from tools.market_data import get_stock_price
from tools.alpaca_tool import place_order, get_portfolio_overview


def build_trading_team(gemini_model_id: str = "gemini-2.0-flash") -> Team:
    # Researcher: fetches market data
    researcher = Agent(
        name="Researcher",
        role="Fetch latest price and recent history for a given ticker.",
        tools=[get_stock_price],
        model=Gemini(id=gemini_model_id),
    )

    # Strategist: analyses and outputs trade signals
    strategist = Agent(
        name="Strategist",
    role=("Receive market and account data and propose a trade signal: 'buy', 'sell' or 'hold' with qty."),
    tools=[get_portfolio_overview],
    model=Gemini(id=gemini_model_id),
    debug_mode=True
    )

    # Executor: executes orders via Alpaca
    executor = Agent(
        name="Executor",
        role="Execute orders via Alpaca or simulate if not configured.",
        tools=[place_order],
        model=Gemini(id=gemini_model_id),
    )

    team = Team(
        name="Trading Team",
        mode="coordinate",
        members=[researcher, strategist, executor],
        model=Gemini(id=gemini_model_id),
        instructions=[
            "Researcher: fetch prices when asked and return structured JSON {symbol, price, time}.",
            "Strategist: always call the portfolio overview tool first to get account state. Then, based on the Researcher's data and portfolio state, propose ONE decision in strict JSON form: {action: 'buy'|'sell'|'hold', symbol: str, qty: int, reason: str, confidence: float (0-1)}.",
            "Safety: if confidence < 0.6, return action 'hold' regardless of other signals.",
            "Executor: if action is 'buy' or 'sell', call place_order(symbol, qty, side) and return the order result. Do NOT execute if the portfolio overview indicates insufficient buying power.",
            "Leader: coordinate members, validate Strategist's JSON, and synthesize final report.",
        ],
        show_members_responses=True,
        markdown=False,
    )

    return team
