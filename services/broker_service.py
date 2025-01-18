import requests
from random import choice

from django.contrib.auth.models import User
from django.db.models import Sum, F

from ex.models import Symbol, Depo, Position, LimitOrder, AbstractOrder
from services.DTO_service import create_random_limit_order_dto
from services.symbol_service import get_best_bid, get_best_ask

DEPO_START_EQUITY = 1_000_000
MAKE_DEAL_CHANCE = 50


def create_deposit(user: User | None = None) -> None:
    depo = Depo.objects.create(
        user=user, start_equity=DEPO_START_EQUITY, current_equity=DEPO_START_EQUITY
    )
    for sym in Symbol.objects.all():
        Position.objects.create(depo=depo, symbol=sym)


def create_deposits(amount: int) -> None:
    for i in range(amount):
        create_deposit()


def get_pnl(position: Position) -> float:
    if position.quantity == 0:
        return 0
    actual_price = (
        get_best_bid(position.symbol)
        if position.sign == 1
        else get_best_ask(position.symbol)
    )
    return round(position.quantity * (actual_price - position.average_price), 2)


def open_orders_equity(depo):
    return (
        LimitOrder.objects.select_related("initiator")
        .filter(initiator=depo, status=AbstractOrder.OrderStatus.PLACED)
        .aggregate(total_equity=Sum(F("quantity") * F("price")))["total_equity"]
        or 0
    )


def equity(position):
    return abs(position.quantity * position.average_price) + get_pnl(position)


def free_equity(depo):
    positions = Position.objects.select_related("depo").filter(depo=depo)
    return (
        depo.current_equity
        - sum([equity(pos) for pos in positions])
        - open_orders_equity(depo)
    )


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
            requests.post(url, json=order.model_dump())
