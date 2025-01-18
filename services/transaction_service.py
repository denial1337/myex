from typing import List

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from ex.models import (
    Transaction,
    LimitOrder,
    MarketOrder,
    AbstractOrder,
    Position,
)
from services.order_validation_service import is_valid_order
from services.socket_service import send_order_book_update, send_new_transaction
from services.symbol_service import (
    update_best_bidask,
    get_ask_limit_orders,
    get_bid_limit_orders, get_best_ask, get_best_bid,
)

TRANSACTIONS_LIMIT = 20


def get_last_transactions(ticker: str) -> List[Transaction]:
    return Transaction.objects.filter(ticker=ticker).order_by("-datetime")[
        :TRANSACTIONS_LIMIT
    ]


def _push_ending_condition_for_market_order(order: MarketOrder) -> bool:
    return order.quantity == 0


def _push_ending_condition_for_buy_limit_order(order: LimitOrder) -> bool:
    return order.quantity == 0 or get_best_ask(order.symbol) > order.price


def _push_ending_condition_for_sell_limit_order(order: LimitOrder) -> bool:
    return order.quantity == 0 or get_best_bid(order.symbol) < order.price


def _push_taker_order(order, get_maker_orders_func, push_ending_condition) -> None:
    """taker order - market order or limit order with price higher(lower) than ask(bid)"""
    while not push_ending_condition(order):
        maker_orders = get_maker_orders_func(order.symbol)
        for maker_order in maker_orders:
            make_market_transaction(maker_order, order)
            if order.status == AbstractOrder.OrderStatus.FILLED:
                update_best_bidask(order.symbol)
                return
        update_best_bidask(order.symbol)


def _update_positions_after_transaction(transaction: Transaction) -> None:
    maker_pos = _get_position_by_order(transaction.maker_order)
    taker_pos = _get_position_by_order(transaction.taker_order)
    if maker_pos is None or taker_pos is None:
        raise ObjectDoesNotExist

    if transaction.maker_order.direction == AbstractOrder.OrderDirection.BUY:
        maker_pos.update_position(transaction.price, transaction.volume)
        taker_pos.update_position(transaction.price, -transaction.volume)
        return

    if transaction.maker_order.direction == AbstractOrder.OrderDirection.SELL:
        maker_pos.update_position(transaction.price, -transaction.volume)
        taker_pos.update_position(transaction.price, transaction.volume)


# FIXME сделать протектед?
def make_market_transaction(maker_order: LimitOrder, taker_order: AbstractOrder) -> None:
    orders_quantity_dif = maker_order.quantity - taker_order.quantity
    content_type = None
    match taker_order:
        case LimitOrder():
            content_type = ContentType.objects.get_for_model(LimitOrder)
        case MarketOrder():
            content_type = ContentType.objects.get_for_model(MarketOrder)

    object_id = taker_order.pk

    transaction = Transaction.objects.create(
        ticker=maker_order.symbol.ticker,
        price=maker_order.price,
        volume=min(taker_order.quantity, maker_order.quantity),
        maker_order=maker_order,
        taker_object_id=object_id,
        taker_content_type=content_type,
    )

    _update_positions_after_transaction(transaction)

    maker_order.quantity = max(0, orders_quantity_dif)
    if maker_order.quantity == 0:
        maker_order.status = AbstractOrder.OrderStatus.FILLED
    maker_order.save()

    taker_order.quantity = -min(0, orders_quantity_dif)
    if taker_order.quantity == 0:
        taker_order.status = AbstractOrder.OrderStatus.FILLED
    taker_order.save()
    send_new_transaction(transaction)


def resolve_order(order: AbstractOrder) -> None:
    if not is_valid_order(order):
        order.status = AbstractOrder.OrderStatus.REJECTED
        order.save()
        return
    if isinstance(order, MarketOrder):
        _resolve_market_order(order)
    if isinstance(order, LimitOrder):
        _resolve_limit_order(order)

    update_best_bidask(order.symbol)


def close_order(order_pk: int) -> bool:
    order = LimitOrder.objects.get(pk=order_pk)

    if order.status == AbstractOrder.OrderStatus.CANCELED:
        return False
    if order.status == AbstractOrder.OrderStatus.PLACED:
        order.status = AbstractOrder.OrderStatus.CANCELED
        order.save()

    return True


def _resolve_market_order(order: MarketOrder) -> None:
    if order.direction == AbstractOrder.OrderDirection.BUY:
        _push_taker_order(order, get_ask_limit_orders, _push_ending_condition_for_market_order)
    elif order.direction == AbstractOrder.OrderDirection.SELL:
        _push_taker_order(order, get_bid_limit_orders, _push_ending_condition_for_market_order)

    if order.quantity == 0:
        order.status = AbstractOrder.OrderStatus.FILLED
        order.save()


def _resolve_limit_order(order: LimitOrder) -> None:
    if order.direction == LimitOrder.OrderDirection.BUY and order.price >= get_best_ask(
        order.symbol
    ):
        _push_taker_order(order, get_ask_limit_orders, _push_ending_condition_for_buy_limit_order)
    elif (
        order.direction == LimitOrder.OrderDirection.SELL
        and order.price <= get_best_bid(order.symbol)
    ):
        _push_taker_order(order, get_bid_limit_orders, _push_ending_condition_for_sell_limit_order)

    order.status = (
        AbstractOrder.OrderStatus.FILLED
        if order.quantity == 0
        else AbstractOrder.OrderStatus.PLACED
    )
    order.save()
    send_order_book_update()


def _get_position_by_order(order: AbstractOrder) -> Position | None:
    depo = order.initiator
    symbol = order.symbol
    return Position.objects.filter(depo=depo, symbol=symbol).first()
