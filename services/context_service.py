from ex.forms.forms import MarketOrderFormManager, LimitOrderFormManager
from services.transaction_service import get_last_transactions


def get_context_by_ticker(ticker: str) -> dict:
    t = get_last_transactions(ticker)
    context = {
        "ticker": ticker,
        "price": [x["price"] for x in list(t.values("price"))[::-1]],
        "datetime": [
            x["datetime"].strftime("%H:%M:%S %m.%d")
            for x in list(t.values("datetime"))[::-1]
        ],  # list(range(len(t))), #
        "market_order_form": MarketOrderFormManager.form,
        "limit_order_form": LimitOrderFormManager.form,
    }
    return context
