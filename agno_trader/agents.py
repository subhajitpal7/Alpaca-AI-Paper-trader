
from agno.agent import Agent
from agno.models.google import Gemini
from agno.team import Team

from tools.alpaca_tool import get_positions, get_portfolio_overview, place_order
from agno.tools.yfinance import YFinanceTools
from tools.market_data import get_stock_price, get_stock_fundamentals, get_multiple_stock_prices

def build_trading_team(gemini_model_id: str = "gemini-1.5-flash") -> Team:
    # 1. Researcher Agent: Gathers and validates data
    researcher = Agent(
        name="Researcher",
        role=(
            "You are a Senior Financial Data Analyst. Your primary responsibility is to gather, clean, and cross-validate financial data from multiple sources to ensure its accuracy and reliability. You are extremely thorough and detail-oriented."
        ),
        tools=[
            get_positions,
            YFinanceTools(stock_price=True, stock_fundamentals=True, company_news=True),
            get_stock_price,
            get_multiple_stock_prices,
            get_stock_fundamentals,
        ],
        model=Gemini(id=gemini_model_id),
    )

    # 2. Strategist Agent: Analyzes data and proposes trades
    strategist = Agent(
        name="Strategist",
        role=(
            "You are a Quantitative Trading Strategist. You develop and backtest trading strategies based on financial data. You are analytical, data-driven, and risk-conscious. You make decisions based on evidence, not emotion."
        ),
        tools=[get_portfolio_overview],
        model=Gemini(id=gemini_model_id),
        debug_mode=True,
    )

    # 3. Executor Agent: Executes trades
    executor = Agent(
        name="Executor",
        role=(
            "You are a Trade Execution Specialist. You are responsible for executing trades precisely as instructed, minimizing slippage and errors. You are fast, reliable, and you keep meticulous records."
        ),
        tools=[place_order],
        model=Gemini(id=gemini_model_id),
    )

    # 4. Team Definition with Detailed Workflow
    team = Team(
        name="Trading Team",
        mode="coordinate",
        members=[researcher, strategist, executor],
        model=Gemini(id=gemini_model_id),
        instructions=[
            "## Overall Goal: Execute a systematic, data-driven trading strategy for the entire portfolio.",
            
            "### Step 1: Researcher - Data Gathering and Validation",
            "1. **Get Portfolio**: Use the `get_positions` tool to get the list of all current stock holdings.",
            "2. **Gather Data from Multiple Sources**: For each stock, fetch data from both Yahoo Finance (`YFinanceTools`) and Alpha Vantage (`get_stock_price`, `get_stock_fundamentals`).",
            "3. **Cross-Validate Prices**: Compare the prices from both sources. If the discrepancy is > 2%, add a `price_discrepancy: true` flag to the output for that stock.",
            "4. **Structure Output**: For each stock, create a detailed JSON object containing: `symbol`, `yfinance_price`, `alphavantage_price`, `price_discrepancy`, `yfinance_fundamentals`, `alphavantage_fundamentals`, and a `news_summary`. Compile these into a single list.",

            "### Step 2: Strategist - Analysis and Trade Generation",
            "1. **Assess Portfolio Health**: Use `get_portfolio_overview` to check current buying power, equity, and market exposure.",
            "2. **Analyze Validated Data**: For each stock object from the Researcher, analyze the fundamental data and news. Pay close attention to `price_discrepancy` flags.",
            "3. **Propose Trades**: Based on your analysis, decide on an action: `BUY`, `SELL`, or `HOLD`. For `BUY`/`SELL`, determine a `qty` that does not expose more than 5% of total portfolio equity to a single asset.",
            "4. **Structure Output**: Generate a list of trade proposals in a strict JSON format: `[{'action': 'BUY'|'SELL'|'HOLD', 'symbol': str, 'qty': int, 'reason': 'Detailed explanation referencing specific data points', 'confidence': float (0.0-1.0)}, ...]",

            "### Step 3: Leader - Final Review and Safety Check",
            "1. **Validate JSON**: Ensure the Strategist's output is valid JSON.",
            "2. **Apply Safety Rules**: Review the confidence score for each proposed trade. If `confidence < 0.7`, downgrade the action to `HOLD`. This is a critical safety measure.",

            "### Step 4: Executor - Trade Execution",
            "1. **Execute Orders**: For each `BUY` or `SELL` trade approved by the Leader, call the `place_order` tool with the correct `symbol`, `qty`, and `side`.",
            "2. **Report Results**: Compile a list of all order confirmation results from the `place_order` tool. If an order fails, report the error clearly.",

            "### Step 5: Leader - Final Synthesis",
            "1. **Synthesize Final Report**: As the Portfolio Manager, create a final, human-readable Markdown report summarizing the entire process: key data findings, trades proposed, safety checks applied, execution results, and the final portfolio status."
        ],
        show_members_responses=True,
        markdown=False,
    )

    return team
