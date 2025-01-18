from services.symbol_service import (
    update_best_bidask,
    get_best_ask,
    get_best_bid,
)
from ex.models import LimitOrder, Symbol, AbstractOrder

MAX_LIMIT = 1000
MIN_LIMIT = 0
DEPTH = 10


def get_serialized_order_book(symbol: Symbol) -> dict:
    result = {}
    update_best_bidask(symbol)
    best_ask = get_best_ask(Symbol.objects.get(ticker=symbol.ticker))
    best_bid = get_best_bid(Symbol.objects.get(ticker=symbol.ticker))

    ask_prices = list(range(best_ask + DEPTH - 1, best_ask - 1, -1))
    asks = [
        LimitOrder.objects.select_related("symbol")
        .filter(
            direction=AbstractOrder.OrderDirection.SELL,
            status=AbstractOrder.OrderStatus.PLACED,
            price=p,
            symbol__ticker=symbol.ticker,
        )
        .values("quantity")
        for p in ask_prices
    ]

    ask_num = [sum([x["quantity"] for x in k]) for k in asks]

    result["ask"] = {}
    result["ask"]["price"] = ask_prices
    result["ask"]["num"] = ask_num

    bid_prices = list(range(best_bid, best_bid - DEPTH, -1))
    bids = [
        LimitOrder.objects.select_related("symbol")
        .filter(
            direction=AbstractOrder.OrderDirection.BUY,
            status=AbstractOrder.OrderStatus.PLACED,
            price=p,
            symbol__ticker=symbol.ticker,
        )
        .values("quantity")
        for p in bid_prices
    ]
    bid_num = [sum([x["quantity"] for x in k]) for k in bids]

    result["bid"] = {}
    result["bid"]["price"] = bid_prices
    result["bid"]["num"] = bid_num

    return result
