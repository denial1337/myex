import enum
import json

from django.shortcuts import get_object_or_404
from pydantic import BaseModel
import random
from random import randint

from ex.models import Depo, MarketOrder, AbstractOrder, Symbol, LimitOrder

MAX_INT = 31**2 - 1


class OrderDirection(enum.Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class OrderType(enum.Enum):
    LIMIT_ORDER = 'limit'
    MARKET_ORDER = 'market'
    STOP_ORDER = 'stop'
    TAKE_ORDER = 'take'


class SymbolPydantic(BaseModel):
    pass

class OrderDTO(BaseModel):
    dir : str
    ticker : str
    quantity : int
    depo_pk: int
    order_type: str


class MarketOrderDTO(OrderDTO):
    pass


class LimitOrderDTO(OrderDTO):
    price_delta : float


def create_dto_market_order(depo_pk, ticker) -> MarketOrderDTO:
    return MarketOrderDTO(depo_pk=depo_pk, order_type = OrderType.MARKET_ORDER,
                          ticker=ticker, dir = random.choice(list(OrderDirection)).value,
                          quantity=randint(3,20))

def create_dto_limit_order(depo_pk, ticker) -> LimitOrderDTO:
    delta = randint(0, 20)
    return LimitOrderDTO(depo_pk=depo_pk, order_type = OrderType.LIMIT_ORDER,
                         ticker=ticker, dir = random.choice(list(OrderDirection)).value,
                         quantity=randint(3,20),
                         price_delta=delta)



def _unpack_dto_to_kwargs(dto : OrderDTO) -> dict:
    d = dict()
    d['initiator'] = get_object_or_404(Depo, pk=dto.depo_pk)
    d['symbol'] = get_object_or_404(Symbol, ticker=dto.ticker)
    d['quantity'] = dto.quantity

    match dto.dir:
        case 'BUY':
            d['dir'] = AbstractOrder.OrderDirection.BUY
        case 'SELL':
            d['dir'] = AbstractOrder.OrderDirection.SELL
        case _:
            raise ValueError(f"expect 'BUY' or 'SELL' but {dto.dir} recived")

    return d



def _dto_to_market_order(dto : MarketOrderDTO):
    kwargs = _unpack_dto_to_kwargs(dto)
    return MarketOrder.objects.create(**kwargs)

def _dto_to_limit_order(dto : LimitOrderDTO):
    kwargs = _unpack_dto_to_kwargs(dto)
    price = 0
    match kwargs['dir']:
        case AbstractOrder.OrderDirection.BUY:
            price = kwargs['symbol'].best_bid - dto.price_delta
            kwargs['price'] = max(0, min(price, MAX_INT))
        case AbstractOrder.OrderDirection.SELL:
            price = kwargs['symbol'].best_ask + dto.price_delta

    kwargs['price'] = max(0, min(price, MAX_INT))

    return LimitOrder.objects.create(**kwargs)


def dto_to_order(dto):
    print(dto)
    match dto:
        case LimitOrderDTO():
            return _dto_to_limit_order(dto)
        case MarketOrderDTO():
            return _dto_to_market_order(dto)
        case _:
            raise TypeError(f'Expected LimitOrderDTO or MarketOrderDTO but {type(dto)} recieved')

def request_to_dto(request):
    data = json.loads(request.body)
    #order_type = data.pop('order_type')
    match data['order_type']:
        case OrderType.LIMIT_ORDER.value:
            return LimitOrderDTO(**data)
        case OrderType.MARKET_ORDER.value:
            return MarketOrderDTO(**data)
        case _:
            raise TypeError(f'OrderType expected but {type(data)} recieved')

def requset_to_order(dto):
    print(dto)
    match dto['order_type']:
        case OrderType.LIMIT_ORDER.value:
            return _dto_to_limit_order(dto)
        case OrderType.MARKET_ORDER.value:
            return _dto_to_market_order(dto)
        case _:
            raise TypeError(f'OrderType expected but {type(dto)} recieved')


