import argparse

from dotenv import load_dotenv

from .agents import build_trading_team

# Load .env if present
load_dotenv()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "symbol", help="Ticker symbol to analyze", default="AAPL", nargs="?"
    )
    parser.add_argument("--model", help="Gemini model id", default="gemini-2.0-flash")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Enable live Alpaca orders (use with caution)",
    )
    args = parser.parse_args()

    team = build_trading_team(gemini_model_id=args.model)

    # Example composite prompt: research price, propose trade and execute.
    task = (
        f"Analyze {args.symbol} and get the account details  and suggest a paper trade."
    )
    print("Running trading team for:", args.symbol)
    report = team.print_response(task, stream=True)
    print(report)


if __name__ == "__main__":
    main()
