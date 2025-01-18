from ex.models import AbstractOrder, MarketOrder, LimitOrder
from services.broker_service import free_equity
from services.symbol_service import bid_count, ask_count


def _get_average_price_for_market_order(order: AbstractOrder) -> int:
    # FIXME
    # тут некоторое допущение, я пропущу сложную агрегацию для вычисления
    # средней цены рыночной заявки и просто возьму лучшую цену
    return (
        ask_count(order.symbol)
        if order.direction == AbstractOrder.OrderDirection.BUY
        else bid_count(order.symbol)
    )


def _get_maker_price(order: AbstractOrder) -> int | None:
    match order:
        case MarketOrder():
            return (
                ask_count(order.symbol)
                if order.direction == AbstractOrder.OrderDirection.BUY
                else bid_count(order.symbol)
            )
        case LimitOrder():
            return order.price
        case _:
            return None


def _is_valid_market_order(order: MarketOrder) -> bool:
    if free_equity(
        order.initiator
    ) < order.quantity * _get_average_price_for_market_order(order):
        return False

    maker_orders_count = (
        ask_count(order.symbol)
        if order.direction == AbstractOrder.OrderDirection.BUY
        else bid_count(order.symbol)
    )

    if order.quantity > maker_orders_count:
        return False

    return True


def _is_valid_limit_order(order: LimitOrder) -> bool:
    depo = order.initiator
    maker_price = _get_maker_price(order)

    return free_equity(depo) > order.quantity * maker_price


# FIXME подправить валидацию для обратной сделки
def is_valid_order(order: AbstractOrder) -> bool:
    match order:
        case LimitOrder():
            return _is_valid_limit_order(order)
        case MarketOrder():
            return _is_valid_market_order(order)
        case _:
            raise ValueError(
                f"LimitOrder or MarketOrder instance expected but {type(order)} recieved"
            )
