from ex.models import LimitOrder, Symbol, AbstractOrder
from django.core.exceptions import ObjectDoesNotExist

def get_symbol_by_ticker(ticker):
    symbol = None
    try:
        symbol = Symbol.objects.get(ticker=ticker)
    except ObjectDoesNotExist as e:
        print(f'ticker "{ticker}" does not exist')
    finally:
        return symbol


def get_ask(symbol):
    return (LimitOrder.objects.select_related('symbol').
            filter(symbol__ticker=symbol.ticker, price=symbol.best_ask,
                   dir=AbstractOrder.OrderDirection.SELL,
                   status=AbstractOrder.OrderStatus.PLACED).
            order_by('datetime'))


def get_bid(symbol):
    return (LimitOrder.objects.select_related('symbol').
            filter(symbol__ticker=symbol.ticker, price=symbol.best_bid,
                   dir=AbstractOrder.OrderDirection.BUY,
                   status=AbstractOrder.OrderStatus.PLACED).
            order_by('datetime'))


def is_active_ask_orders_exist(symbol):
    return (LimitOrder.objects.select_related('symbol').
                filter(symbol__ticker=symbol.ticker,
                       dir=AbstractOrder.OrderDirection.SELL,
                       status=AbstractOrder.OrderStatus.PLACED).
            exists())


def is_active_bid_orders_exist(symbol):
    return (LimitOrder.objects.select_related('symbol').
            filter(symbol__ticker=symbol.ticker,
                   dir=AbstractOrder.OrderDirection.BUY,
                   status=AbstractOrder.OrderStatus.PLACED).exists())


def update_best_bidask(symbol):
    if is_active_ask_orders_exist(symbol):
        symbol.best_ask = (LimitOrder.objects.select_related('symbol').
                           filter( symbol__ticker = symbol.ticker,
                                   dir=AbstractOrder.OrderDirection.SELL,
                                   status=AbstractOrder.OrderStatus.PLACED).
                           order_by('price').first().price)

    if is_active_bid_orders_exist(symbol):
        symbol.best_bid = (LimitOrder.objects.select_related('symbol').
                           filter( symbol__ticker = symbol.ticker,
                                   dir=AbstractOrder.OrderDirection.BUY,
                                   status=AbstractOrder.OrderStatus.PLACED).
                           order_by('price').last().price)
    symbol.save()


def set_default_bidask(symbol):
    symbol.best_ask = 2 ** 31 - 1
    symbol.best_bid = 0