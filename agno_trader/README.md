Agno Trading Team — Paper Trading Demo

This folder contains a minimal Agno-based trading team that:
- fetches stock data
- decides trades using a Gemini model
- executes paper trades via Alpaca (or simulates when no keys provided)

Requirements
- Python 3.10+ recommended
- Set environment variables before running (PowerShell examples below)

PowerShell quick start

```powershell
# create venv and activate
python -m venv .venv
. .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\agno_trader\requirements.txt

# export keys (replace placeholders)
$env:GOOGLE_API_KEY = 'YOUR_GOOGLE_API_KEY'
$env:ALPACA_API_KEY = 'YOUR_ALPACA_API_KEY'
$env:ALPACA_SECRET = 'YOUR_ALPACA_SECRET'
$env:ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'

# run the demo
python -m agno_trader.main
```

Notes
- The demo will simulate order execution if Alpaca keys are not set.
- Configure `GOOGLE_API_KEY` (or Vertex settings) to use Gemini.
- This is a starter scaffold — test thoroughly before using with real money.
