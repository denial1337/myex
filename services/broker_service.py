import time
import requests
from random import randint, choice

from ex.models import Symbol, Depo
from services.DTO_service import create_dto_market_order, create_dto_limit_order

MAKE_DEAL_CHANCE = 5


def start_trading():
    print('TRADING STARTS')
    deposits = Depo.objects.filter(user=None)
    tickers = [ i['ticker'] for i in list(Symbol.objects.all().values('ticker')) ]
    print('tickers', tickers)
    for i in range(200):
        print(i)
        for depo in deposits:
            r = randint(0, 100)
            #print('rand',r)
            if r > MAKE_DEAL_CHANCE:
                continue
            ticker = choice(tickers)

            url = f'http://127.0.0.1:8000/api/{ticker}/'
            order = create_dto_limit_order(depo.pk, ticker)
            req = requests.post(url, json=order.model_dump())
            print(req.status_code, req.json())
            time.sleep(1)







