from typing import List

from django.db.models import Sum

from ex.models import LimitOrder, Symbol, AbstractOrder
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache


def get_symbol_by_ticker(ticker: str) -> Symbol:
    symbol = cache.get(ticker)
    if symbol:
        print("return from redis")
        return symbol

    try:
        symbol = Symbol.objects.get(ticker=ticker)
        cache.set(ticker, symbol)
    except ObjectDoesNotExist:
        print(f'ticker "{ticker}" does not exist')
    finally:
        return symbol


def get_best_bid(symbol: Symbol) -> int:
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


def get_best_ask(symbol: Symbol) -> int:
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


def bid_count(symbol: Symbol) -> int:
    return (
        LimitOrder.objects.filter(
            direction=AbstractOrder.OrderDirection.BUY,
            status=AbstractOrder.OrderStatus.PLACED,
            symbol=symbol,
        ).aggregate(Sum("quantity"))["quantity__sum"]
        or 0
    )


def ask_count(symbol: Symbol) -> int:
    return (
        LimitOrder.objects.filter(
            direction=AbstractOrder.OrderDirection.SELL,
            status=AbstractOrder.OrderStatus.PLACED,
            symbol=symbol,
        ).aggregate(Sum("quantity"))["quantity__sum"]
        or 0
    )


def get_ask_limit_orders(symbol: Symbol) -> List[LimitOrder]:
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


def get_bid_limit_orders(symbol: Symbol) -> List[LimitOrder]:
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


def is_active_ask_orders_exist(symbol: Symbol) -> bool:
    return (
        LimitOrder.objects
        .filter(
            symbol__ticker=symbol.ticker,
            direction=AbstractOrder.OrderDirection.SELL,
            status=AbstractOrder.OrderStatus.PLACED,
        )
        .exists()
    )


def is_active_bid_orders_exist(symbol: Symbol) -> bool:
    return (
        LimitOrder.objects
        .filter(
            symbol__ticker=symbol.ticker,
            direction=AbstractOrder.OrderDirection.BUY,
            status=AbstractOrder.OrderStatus.PLACED,
        )
        .exists()
    )


def update_best_bidask(symbol: Symbol) -> None:
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


def set_default_bidask_for_all_symbols() -> None:
    for sym in Symbol.objects.all():
        set_default_bidask(sym)


def set_default_bidask(symbol: Symbol) -> None:
    symbol.best_ask = 2**31 - 1
    symbol.best_bid = 0
