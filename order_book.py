from ex.models import LimitOrder#, OrderBook
from random import randint
MAX_LIMIT = 1000
MIN_LIMIT = 0
DEPTH = 5

class OrderBook(object):
    """class for reading and handle limit orders"""
    def __init__(self, symbol):
        print("INIT CALLED")
        """Bid - long | Ask - short"""
        self.symbol=symbol
        self.best_ask = -1
        self.best_bid = -1
        if orders := LimitOrder.objects.filter(dir="sell", symbol=symbol).order_by('price'):
            self.best_ask = orders.first().price
        if orders := LimitOrder.objects.filter(dir="buy", symbol=symbol).order_by('price'):
            self.best_bid = orders.last().price
        if self.best_ask == -1 and self.best_bid != -1:
            self.best_ask = self.best_bid + 1
        if self.best_bid == -1 and self.best_ask != -1:
            self.best_bid = self.best_ask - 1

    def get_ask(self):
        return LimitOrder.objects.filter(dir="sell", symbol=self.symbol, price=self.best_ask).order_by('datetime')
    def get_bid(self):
        return LimitOrder.objects.filter(dir="buy", symbol=self.symbol, price=self.best_bid).order_by('datetime')

    def update_best_bidask(self):
        if self.is_ask_orders_exist():
            self.best_ask = LimitOrder.objects.filter(dir="sell", symbol=self.symbol).order_by('price').first().price
        if self.is_bid_orders_exist():
            self.best_bid = LimitOrder.objects.filter(dir="buy", symbol=self.symbol).order_by('price').last().price

    def is_ask_orders_exist(self):
        return LimitOrder.objects.filter(symbol=self.symbol, dir='sell').exists()

    def is_bid_orders_exist(self):
        return LimitOrder.objects.filter(symbol=self.symbol, dir='buy').exists()

    def __str__(self):
        ask_prices = range(self.best_ask + DEPTH - 1, self.best_ask - 1, -1)
        asks = [LimitOrder.objects.filter(dir="sell", price=p, symbol=self.symbol).values('quantity')
                for p in ask_prices]
        asks_num = [sum([x['quantity'] for x in k]) for k in asks]
        s = ''.join([f'{p} : {a}\n' for p,a in zip(ask_prices, asks_num)])

        s += '-' * 10 + '\n'

        bid_prices = range(self.best_bid, self.best_bid - DEPTH, -1)
        bids = [LimitOrder.objects.filter(dir="buy", price=p, symbol=self.symbol).values('quantity')
                for p in bid_prices]
        bid_num = [sum([x['quantity'] for x in k]) for k in bids]
        s += ''.join([f'{p} : {a}\n' for p, a in zip(bid_prices, bid_num)])
        return s

