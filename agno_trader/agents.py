from agno.agent import Agent
from agno.models.google import Gemini
from agno.team import Team

from tools.alpaca_tool import place_order, get_portfolio_overview, get_positions
from agno.tools.yfinance import YFinanceTools


def build_trading_team(gemini_model_id: str = "gemini-2.0-flash") -> Team:
    # Researcher: fetches market data and fundamentals for the entire portfolio
    researcher = Agent(
        name="Researcher",
        role="Fetch latest prices and fundamental data for all stocks in the portfolio.",
        tools=[
            get_positions,
            YFinanceTools(
                stock_price=True, stock_fundamentals=True, company_news=True
            ),
        ],
        model=Gemini(id=gemini_model_id),
    )

    # Strategist: analyses and outputs trade signals for the entire portfolio
    strategist = Agent(
        name="Strategist",
        role="Analyze the portfolio, market data, and fundamental data to propose a list of trades (buy, sell, or hold) for each stock.",
        tools=[get_portfolio_overview],
        model=Gemini(id=gemini_model_id),
        debug_mode=True,
    )

    # Executor: executes a list of orders via Alpaca
    executor = Agent(
        name="Executor",
        role="Execute a list of orders via Alpaca or simulate if not configured.",
        tools=[place_order],
        model=Gemini(id=gemini_model_id),
    )

    team = Team(
        name="Trading Team",
        mode="coordinate",
        members=[researcher, strategist, executor],
        model=Gemini(id=gemini_model_id),
        instructions=[
            "Researcher: first, get all positions using the get_positions tool. Then, for each position, fetch the latest price using the get_stock_price tool, the fundamental data using the get_stock_fundamentals tool, and the latest news using the get_company_news tool. Finally, return a list of structured JSON objects, each containing the symbol, price, the full fundamental data object, and news.",
            "Strategist: always call the portfolio overview tool first to get the current account state. Then, based on the Researcher's data (including prices and fundamentals) and the overall portfolio health, propose a list of trade decisions in strict JSON form: [{action: 'buy'|'sell'|'hold', symbol: str, qty: int, reason: str, confidence: float (0-1)}, ...]. The reason should explicitly mention the key fundamentals that support the decision.",
            "Safety: if confidence < 0.6 for any proposed trade, change the action to 'hold' for that trade.",
            "Executor: for each trade in the list from the Strategist, if the action is 'buy' or 'sell', call the place_order tool with the correct parameters. Return a list of the order results.",
            "Leader: coordinate the members, validate the JSON from the Strategist, and synthesize a final report of all actions taken.",
        ],
        show_members_responses=True,
        markdown=False,
    )

    return team
