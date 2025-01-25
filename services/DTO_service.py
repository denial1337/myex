import enum
import json

from django.http import HttpRequest
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from pydantic import BaseModel
import random
from random import randint

from ex.forms.forms import MarketOrderForm, LimitOrderForm
from ex.models import Depo, MarketOrder, AbstractOrder, Symbol, LimitOrder
from services.symbol_service import get_symbol_by_ticker

MAX_INT = 31**2 - 1


class OrderDirection(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(enum.Enum):
    LIMIT_ORDER = "limit"
    MARKET_ORDER = "market"
    STOP_ORDER = "stop"
    TAKE_ORDER = "take"


class SymbolPydantic(BaseModel):
    pass


class OrderDTO(BaseModel):
    direction: str
    ticker: str
    quantity: int
    depo_pk: int  # FIXME мб передавать сам депозит, а не пк
    order_type: str


class MarketOrderDTO(OrderDTO):
    pass


class LimitOrderDTO(OrderDTO):
    price: float


def create_market_order_dto(depo_pk: int, ticker: str) -> MarketOrderDTO:
    return MarketOrderDTO(
        depo_pk=depo_pk,
        order_type=OrderType.MARKET_ORDER,
        ticker=ticker,
        direction=random.choice(list(OrderDirection)).value,
        quantity=randint(3, 20),
    )


def create_random_limit_order_dto(depo_pk: int, ticker: str) -> LimitOrderDTO:
    delta = randint(-20, 20)
    return LimitOrderDTO(
        depo_pk=depo_pk,
        order_type=OrderType.LIMIT_ORDER,
        ticker=ticker,
        direction=random.choice(list(OrderDirection)).value,
        quantity=randint(3, 20),
        price=500 + delta,
    )


def _unpack_dto_to_kwargs(dto: OrderDTO) -> dict:
    d = dict()
    d["initiator"] = get_object_or_404(Depo, pk=dto.depo_pk)
    d["symbol"] = get_object_or_404(Symbol, ticker=dto.ticker)
    d["quantity"] = dto.quantity

    match dto.direction:
        case "BUY":
            d["direction"] = AbstractOrder.OrderDirection.BUY
        case "SELL":
            d["direction"] = AbstractOrder.OrderDirection.SELL
        case _:
            raise ValueError(f"expect 'BUY' or 'SELL' but {dto.direction} recived")

    return d


def _dto_to_market_order(dto: MarketOrderDTO) -> MarketOrder:
    kwargs = _unpack_dto_to_kwargs(dto)
    return MarketOrder.objects.create(**kwargs)


def _dto_to_limit_order(dto: LimitOrderDTO) -> LimitOrder:
    kwargs = _unpack_dto_to_kwargs(dto)
    price = 0
    match kwargs["direction"]:
        case AbstractOrder.OrderDirection.BUY:
            price = dto.price
        case AbstractOrder.OrderDirection.SELL:
            price = dto.price

    kwargs["price"] = max(0, min(price, MAX_INT))
    return LimitOrder.objects.create(**kwargs)


def dto_to_order(dto: LimitOrderDTO | MarketOrderDTO):
    match dto:
        case LimitOrderDTO():
            return _dto_to_limit_order(dto)
        case MarketOrderDTO():
            return _dto_to_market_order(dto)
        case _:
            raise TypeError(
                f"Expected LimitOrderDTO or MarketOrderDTO but {type(dto)} recieved"
            )


def api_request_to_dto(request: HttpRequest) -> LimitOrderDTO | MarketOrderDTO:
    data = json.loads(request.body)
    match data["order_type"]:
        case OrderType.LIMIT_ORDER.value:
            return LimitOrderDTO(**data)
        case OrderType.MARKET_ORDER.value:
            return MarketOrderDTO(**data)
        case _:
            raise TypeError(f"OrderType expected but {type(data)} recieved")


def socket_message_to_order(message: dict) -> LimitOrder | MarketOrder:
    ticker = message["ticker"]
    symbol = get_symbol_by_ticker(ticker)
    initiator = get_object_or_404(Depo, user__pk=message["user"])
    depo_pk = initiator.pk
    btn = message["button"]

    direction = (
        OrderDirection.BUY
        if "buy" in btn
        else OrderDirection.SELL
        if "sell" in btn
        else None
    )
    if direction is None:
        raise ValueError(
            'Button name error: expect button with "buy" or "sell" in name'
        )
    order_type = (
        OrderType.LIMIT_ORDER
        if "limit" in btn
        else OrderType.MARKET_ORDER
        if "market" in btn
        else None
    )
    if order_type is None:
        raise ValueError(
            'Button name error: expect button with "limit" or "market" in name'
        )

    match order_type:
        case OrderType.LIMIT_ORDER:
            price = message["form"]["price"]
            quantity = message["form"]["quantity"]
            dto = LimitOrderDTO(**locals())

        case OrderType.MARKET_ORDER:
            quantity = message["form"]["quantity"]
            dto = MarketOrderDTO(**locals())

        case _:
            raise TypeError(f"OrderType expected but {order_type} recieved")

    return dto_to_order(dto)


def view_request_to_order(
    request: HttpRequest, ticker: str
) -> LimitOrder | MarketOrder:
    symbol = get_symbol_by_ticker(ticker)
    initiator = get_object_or_404(Depo, user=request.user)
    depo_pk = initiator.pk
    btn = request.POST["submit_button"]

    direction = (
        OrderDirection.BUY
        if "buy" in btn
        else OrderDirection.SELL
        if "sell" in btn
        else None
    )
    if direction is None:
        raise ValueError(
            'Button name error: expect button with "buy" or "sell" in name'
        )
    order_type = (
        OrderType.LIMIT_ORDER
        if "limit" in btn
        else OrderType.MARKET_ORDER
        if "market" in btn
        else None
    )
    if order_type is None:
        raise ValueError(
            'Button name error: expect button with "limit" or "market" in name'
        )

    match order_type:
        case OrderType.LIMIT_ORDER:
            form = LimitOrderForm(request.POST)
            if not form.is_valid():
                raise ValidationError("There is no valid forms")
            price = form.cleaned_data["price"]
            quantity = form.cleaned_data["quantity"]
            dto = LimitOrderDTO(**locals())

        case OrderType.MARKET_ORDER:
            form = MarketOrderForm(request.POST)
            if not form.is_valid():
                raise ValidationError("There is no valid forms")
            quantity = form.cleaned_data["quantity"]
            dto = MarketOrderDTO(**locals())

        case _:
            raise TypeError(f"OrderType expected but {order_type} recieved")

    return dto_to_order(dto)
