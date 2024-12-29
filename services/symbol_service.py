from asgiref.timeout import timeout
from django.db.models import Sum

from ex.models import LimitOrder, Symbol, AbstractOrder
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache


def get_symbol_by_ticker(ticker):
    symbol = cache.get(ticker)
    if symbol:
        print("return from redis")
        return symbol

    try:
        symbol = Symbol.objects.get(ticker=ticker)
        cache.set(ticker, symbol)
    except ObjectDoesNotExist as e:
        print(f'ticker "{ticker}" does not exist')
    finally:
        return symbol


def get_best_bid(symbol):
    key = "best_bid_" + symbol.ticker
    if best_bid := cache.get(key):
        return best_bid

    if is_active_bid_orders_exist(symbol):
        best_bid = (
            LimitOrder.objects.filter(
                symbol__ticker=symbol.ticker,
                direction=AbstractOrder.OrderDirection.BUY,
                status=AbstractOrder.OrderStatus.PLACED,
            )
            .order_by("price")
            .last()
            .price
        )
    else:
        best_bid = 0
    cache.set(key, best_bid)
    return best_bid


def get_best_ask(symbol):
    key = "best_ask_" + symbol.ticker
    if best_ask := cache.get(key):
        return best_ask
    if is_active_ask_orders_exist(symbol):
        best_ask = (
            LimitOrder.objects
            .filter(
                symbol__ticker=symbol.ticker,
                direction=AbstractOrder.OrderDirection.SELL,
                status=AbstractOrder.OrderStatus.PLACED,
            )
            .order_by("price")
            .first()
            .price
        )
    else:
        best_ask = 2**31 - 1
    cache.set(key, best_ask)
    return best_ask


def bid_count(symbol):
    return (
        LimitOrder.objects.filter(
            direction=AbstractOrder.OrderDirection.BUY,
            status=AbstractOrder.OrderStatus.PLACED,
            symbol=symbol,
        ).aggregate(Sum("quantity"))["quantity__sum"]
        or 0
    )


def ask_count(symbol):
    return (
        LimitOrder.objects.filter(
            direction=AbstractOrder.OrderDirection.SELL,
            status=AbstractOrder.OrderStatus.PLACED,
            symbol=symbol,
        ).aggregate(Sum("quantity"))["quantity__sum"]
        or 0
    )


def get_ask(symbol):
    return (
        LimitOrder.objects
        .filter(
            symbol__ticker=symbol.ticker,
            price=get_best_ask(symbol),
            direction=AbstractOrder.OrderDirection.SELL,
            status=AbstractOrder.OrderStatus.PLACED,
        )
        .order_by("datetime")
    )


def get_bid(symbol):
    return (
        LimitOrder.objects
        .filter(
            symbol__ticker=symbol.ticker,
            price=get_best_bid(symbol),
            direction=AbstractOrder.OrderDirection.BUY,
            status=AbstractOrder.OrderStatus.PLACED,
        )
        .order_by("datetime")
    )


def is_active_ask_orders_exist(symbol):
    return (
        LimitOrder.objects
        .filter(
            symbol__ticker=symbol.ticker,
            direction=AbstractOrder.OrderDirection.SELL,
            status=AbstractOrder.OrderStatus.PLACED,
        )
        .exists()
    )


def is_active_bid_orders_exist(symbol):
    return (
        LimitOrder.objects
        .filter(
            symbol__ticker=symbol.ticker,
            direction=AbstractOrder.OrderDirection.BUY,
            status=AbstractOrder.OrderStatus.PLACED,
        )
        .exists()
    )


def update_best_bidask(symbol):
    ask_key = "best_ask_" + symbol.ticker
    if is_active_ask_orders_exist(symbol):
        best_ask = (
            LimitOrder.objects
            .filter(
                symbol__ticker=symbol.ticker,
                direction=AbstractOrder.OrderDirection.SELL,
                status=AbstractOrder.OrderStatus.PLACED,
            )
            .order_by("price")
            .first()
            .price
        )
        cache.set(ask_key, best_ask)

    bid_key = "best_bid_" + symbol.ticker
    if is_active_bid_orders_exist(symbol):
        best_bid = (
            LimitOrder.objects.select_related("symbol")
            .filter(
                symbol__ticker=symbol.ticker,
                direction=AbstractOrder.OrderDirection.BUY,
                status=AbstractOrder.OrderStatus.PLACED,
            )
            .order_by("price")
            .last()
            .price
        )
        cache.set(bid_key, best_bid)


def set_default_bidask_for_all_symbols():
    for sym in Symbol.objects.all():
        set_default_bidask(sym)


def set_default_bidask(symbol):
    symbol.best_ask = 2**31 - 1
    symbol.best_bid = 0
