import os
import argparse
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Use package import so module can be executed as a package
from agents import build_trading_team


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol", help="Ticker symbol to analyze", default="AAPL", nargs="?")
    parser.add_argument("--model", help="Gemini model id", default="gemini-2.0-flash")
    parser.add_argument("--live", action="store_true", help="Enable live Alpaca orders (use with caution)")
    args = parser.parse_args()

    # If not running in live mode, ensure Alpaca env vars are not present so the executor simulates orders.
    if not args.live:
        os.environ.pop("ALPACA_API_KEY", None)
        os.environ.pop("ALPACA_SECRET", None)

    team = build_trading_team(gemini_model_id=args.model)

    # Example composite prompt: research price, propose trade and execute.
    task = f"Analyze {args.symbol} and suggest a paper trade."
    print("Running trading team for:", args.symbol)
    report = team.print_response(task, stream=True)
    print(report)


if __name__ == "__main__":
    main()
