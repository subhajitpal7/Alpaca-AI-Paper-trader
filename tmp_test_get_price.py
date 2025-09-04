import json

from agno_trader.tools.alpaca_tool import _get_account_overview_impl

r = _get_account_overview_impl()
print(json.dumps(r, indent=2))
