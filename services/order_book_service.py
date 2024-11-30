from random import randint
import json

from matplotlib.font_manager import json_dump

from services.symbol_service import get_symbol_by_ticker
from ex.models import LimitOrder, Symbol, AbstractOrder

MAX_LIMIT = 1000
MIN_LIMIT = 0
DEPTH = 10



def get_serialized_order_book(symbol):
    result = {}
    best_ask = Symbol.objects.get(ticker=symbol.ticker).best_ask
    best_bid = Symbol.objects.get(ticker=symbol.ticker).best_bid

    ask_prices = range(best_ask + DEPTH - 1, best_ask - 1, -1)
    asks = [LimitOrder.objects.select_related('symbol').
            filter(dir=AbstractOrder.OrderDirection.SELL, status=AbstractOrder.OrderStatus.PLACED,
                   price=p, symbol__ticker=symbol.ticker).values('quantity')
            for p in ask_prices]

    asks_num = [sum([x['quantity'] for x in k]) for k in asks]

    result['ask'] = dict(zip(ask_prices, asks_num))#json.loads(json.dumps(dict(zip(ask_prices, asks_num))))

    bid_prices = range(best_bid, best_bid - DEPTH, -1)
    bids = [LimitOrder.objects.select_related('symbol').
            filter(dir=AbstractOrder.OrderDirection.BUY,status=AbstractOrder.OrderStatus.PLACED,
                   price=p, symbol__ticker=symbol.ticker).values('quantity')
            for p in bid_prices]
    bid_num = [sum([x['quantity'] for x in k]) for k in bids]

    result['bid'] = dict(zip(bid_prices, bid_num))#json.loads(json.dumps(dict(zip(bid_prices, bid_num))))

    # print(result)
    # r = json.dumps(result)
    # print(r)
    # print(json.loads(r))
    return result


def get_order_book_by_ticker(ticker):
    symbol = get_symbol_by_ticker(ticker)
    return get_order_book(symbol)

def get_order_book(symbol):
    best_ask = Symbol.objects.get(ticker=symbol.ticker).best_ask
    best_bid = Symbol.objects.get(ticker=symbol.ticker).best_bid

    ask_prices = range(best_ask + DEPTH - 1, best_ask - 1, -1)
    asks = [LimitOrder.objects.select_related('symbol').
            filter(dir=AbstractOrder.OrderDirection.SELL, status=AbstractOrder.OrderStatus.PLACED,
                   price=p, symbol__ticker=symbol.ticker).values('quantity')
            for p in ask_prices]

    asks_num = [sum([x['quantity'] for x in k]) for k in asks]
    s = ''.join([f'{p} : {a}\n' for p,a in zip(ask_prices, asks_num)])

    s += '-' * 10 + '\n'

    bid_prices = range(best_bid, best_bid - DEPTH, -1)
    bids = [LimitOrder.objects.select_related('symbol').
            filter(dir=AbstractOrder.OrderDirection.BUY,status=AbstractOrder.OrderStatus.PLACED,
                   price=p, symbol__ticker=symbol.ticker).values('quantity')
            for p in bid_prices]
    bid_num = [sum([x['quantity'] for x in k]) for k in bids]
    s += ''.join([f'{p} : {a}\n' for p, a in zip(bid_prices, bid_num)])
    return s

