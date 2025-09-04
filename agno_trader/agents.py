from agno.agent import Agent
from agno.models.google import Gemini
from agno.team import Team
from dotenv import load_dotenv

from .tools.alpaca_tool import get_portfolio_overview, place_order
from .tools.market_data import get_stock_price

# Load environment variables from .env (repository root)
load_dotenv()


def build_trading_team(gemini_model_id: str = "gemini-2.5-flash") -> Team:
    # Researcher: fetches market data
    researcher = Agent(
        name="Researcher",
        role=(
            "Fetch latest price and recent history for a given ticker and also the "
            "account overview."
        ),
        tools=[get_stock_price, get_portfolio_overview],
        model=Gemini(id=gemini_model_id),
        debug_mode=True,
    )

    # Strategist: analyses and outputs trade signals
    strategist = Agent(
        name="Strategist",
        role=(
            "Receive market and account data, and propose a trade signal: 'buy', "
            "'sell' or 'hold' with qty."
        ),
        model=Gemini(id=gemini_model_id),
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
            (
                "Researcher: fetch  and corresponding account details of the user "
                "when asked and return structured JSON {symbol, price, time,{ "
                "account overview: json}}."
            ),
            (
                "Strategist: always call the portfolio overview tool first to get "
                "account state and explain the details. Then, based on the "
                "Researcher's data and portfolio state, propose ONE decision in "
                "strict JSON form: {action: 'buy'|'sell'|'hold', symbol: str, "
                "qty: int, reason: str, confidence: float (0-1)}."
            ),
            (
                "Safety: if confidence < 0.6, return action 'hold' regardless of "
                "other signals."
            ),
            (
                "Executor: if action is 'buy' or 'sell', call place_order(symbol, "
                "qty, side) and return the order result. Do NOT execute if the "
                "portfolio overview indicates insufficient buying power."
            ),
            (
                "Leader: coordinate members, validate Strategist's JSON, and "
                "synthesize final report."
            ),
        ],
        show_members_responses=True,
        markdown=False,
    )

    return team
