import time
import requests
from random import randint, choice

from ex.models import Symbol, Depo
from services.DTO_service import create_random_limit_order_dto

MAKE_DEAL_CHANCE = 50


def create_deposits(amount):
    for i in range(amount):
        Depo.objects.create(start_equity=1_000_000)


def start_trading():
    print("TRADING STARTS")
    deposits = Depo.objects.filter(user=None)
    tickers = [i["ticker"] for i in list(Symbol.objects.all().values("ticker"))]
    for i in range(2000):
        for depo in deposits:
            # r = randint(0, 100)
            # if r > MAKE_DEAL_CHANCE:
            #     continue
            ticker = choice(tickers)

            url = f"http://127.0.0.1:8000/api/{ticker}/"
            order = create_random_limit_order_dto(depo.pk, ticker)
            req = requests.post(url, json=order.model_dump())
