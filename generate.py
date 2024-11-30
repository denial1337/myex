from random import randint, choice
from ex.models import LimitOrder, Symbol, Depo, AbstractOrder  # , OrderBook, OrderLine
from services.transaction_service import resolve_order


def generate_symbols():
    tickers = ['TLST', 'PSH', 'LRMN']
    full = ['TOLSTOY CORP', 'PUSHKIN BANK', 'LERMONT']
    for t, f in zip(tickers, full):
        Symbol.objects.create(ticker=t, full_name=f)


def generate(amount):
    low_price_limit = 1
    top_price_limit = 1000

    ask = [randint(490, 530) for _ in range(amount)]
    bid = [randint(470, 509) for _ in range(amount)]

    #[OrderLine.objects.create(price=x, order_book=ob) for x in range(low_price_limit, top_price_limit)]

    ask_quantity = [randint(3, 50) for _ in range(amount)]
    bid_quantity = [randint(3, 50) for _ in range(amount)]

    print(1)

    symbol = Symbol.objects.get(ticker='TLST')

    [resolve_order(LimitOrder.objects.create(price=p, quantity=q, dir='sell', status=0, symbol=symbol))
     for p, q in zip(ask, ask_quantity)]
    [resolve_order(LimitOrder.objects.create(price=p, quantity=q, dir='buy', status=0, symbol=symbol))
     for p,q in zip(bid, bid_quantity)]


def generate_deposits(amount):
    for i in range(amount):
        equity = randint(10_000, 100_000)
        Depo.objects.create(is_algo=False, start_equity=equity)


def generate_limit_orders():
    direction = [AbstractOrder.OrderDirection.BUY, AbstractOrder.OrderDirection.SELL]
    symbols = Symbol.objects.all()
    print('generation start')
    cnt = 0
    for depo in Depo.objects.all()[:50]:
        print(cnt)
        cnt+=1
        price = randint(490, 530)
        quantity = randint(3, 50)
        d = choice(direction)
        s = choice(symbols)
        order = LimitOrder.objects.create(initiator=depo, price=price, quantity=quantity,
                                          dir=d, symbol=s)
        resolve_order(order)