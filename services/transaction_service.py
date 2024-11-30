from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from ex.models import Transaction, LimitOrder, MarketOrder, AbstractOrder, Position, Depo
from services.order_book_service import *
from services.order_validation_service import is_valid_order
from services.symbol_service import update_best_bidask, get_ask, is_active_ask_orders_exist, get_bid, \
    is_active_bid_orders_exist

TRANSACTIONS_LIMIT = 20



def get_last_transactions(ticker):
    return Transaction.objects.filter(ticker=ticker).order_by('-datetime')[:TRANSACTIONS_LIMIT]

def push_ending_condition_for_market_order(order):
    return order.quantity == 0

def push_ending_condition_for_buy_limit_order(order):
    return order.quantity == 0 or order.symbol.best_ask > order.price

def push_ending_condition_for_sell_limit_order(order):
    return order.quantity == 0 or order.symbol.best_bid < order.price

def push_taker_order(order, get_make_orders_func, orders_existing_func, push_ending_condition):
    """taker order - market order or limit order with price higher(lower) than ask(bid)"""
    while not push_ending_condition(order):
        maker_orders = get_make_orders_func(order.symbol)
        #print('push start')
        for maker_order in maker_orders:
            make_market_transaction(maker_order, order)
            if maker_order.quantity == 0:
                maker_order.status = AbstractOrder.OrderStatus.FILLED
                maker_order.save()
            #print(order.symbol.best_ask, order.symbol.best_bid)
            update_best_bidask(order.symbol)



def create_and_push_market_order(symbol, direction, quantity):
    #print(symbol, direction, quantity)
    mo = MarketOrder(dir=direction, quantity=quantity, symbol=symbol)
    mo.save()
    resolve_order(mo)
    return mo.status


def create_and_push_limit_order(symbol, direction, quantity, price):
    #print(symbol, direction, quantity, price)
    lo = LimitOrder(dir=direction, quantity=quantity, price=price, symbol=symbol)
    lo.save()
    resolve_order(lo)
    return lo.status


def update_positions_after_transaction(transaction : Transaction):
    maker_pos = get_position_by_order(transaction.maker_order)
    taker_pos = get_position_by_order(transaction.taker_order)
    if maker_pos is None or taker_pos is None:
        raise ObjectDoesNotExist

    if transaction.maker_order.dir == AbstractOrder.OrderDirection.BUY:
        maker_pos.update_position(transaction.price, transaction.volume)
        taker_pos.update_position(transaction.price, -transaction.volume)

    if transaction.maker_order.dir == AbstractOrder.OrderDirection.SELL:
        maker_pos.update_position(transaction.price, -transaction.volume)
        taker_pos.update_position(transaction.price, transaction.volume)

def make_market_transaction(maker_order : LimitOrder, taker_order : AbstractOrder):
    orders_quantity_dif = maker_order.quantity - taker_order.quantity
    content_type = None
    match taker_order:
        case LimitOrder():
            content_type = ContentType.objects.get_for_model(LimitOrder)
        case MarketOrder():
            content_type = ContentType.objects.get_for_model(MarketOrder)

    if content_type is None:
        raise ValueError

    object_id = taker_order.pk

    transaction = Transaction.objects.create(ticker=maker_order.symbol.ticker,
                                             price=maker_order.price,
                                             volume=min(taker_order.quantity, maker_order.quantity),
                                             maker_order=maker_order,
                                             taker_object_id=object_id, taker_content_type=content_type)

    #update_positions_after_transaction(transaction)

    maker_order.quantity = max(0, orders_quantity_dif)
    maker_order.save()
    taker_order.quantity = -min(0, orders_quantity_dif)
    taker_order.save()


def resolve_order(order):
    if not is_valid_order(order):
        order.status = AbstractOrder.OrderStatus.REJECTED
        order.save()
        return
    if isinstance(order, MarketOrder):
        _resolve_market_order(order)
    if isinstance(order, LimitOrder):
        _resolve_limit_order(order)
    update_best_bidask(order.symbol)
    #print('resolve_done')



def _resolve_market_order(order : MarketOrder):
    if order.dir == AbstractOrder.OrderDirection.BUY:
        push_taker_order(order, get_ask, is_active_ask_orders_exist, push_ending_condition_for_market_order)
    elif order.dir == AbstractOrder.OrderDirection.SELL:
        push_taker_order(order, get_bid, is_active_bid_orders_exist, push_ending_condition_for_market_order)

    if order.quantity == 0:
        order.status = AbstractOrder.OrderStatus.FILLED
        order.save()


def _resolve_limit_order(order : LimitOrder):
    if order.dir == LimitOrder.OrderDirection.BUY and order.price >= order.symbol.best_ask:
            push_taker_order(order, get_ask, is_active_ask_orders_exist,
                             push_ending_condition_for_buy_limit_order)
    elif order.dir == LimitOrder.OrderDirection.SELL and order.price <= order.symbol.best_bid:
            push_taker_order(order, get_bid, is_active_bid_orders_exist,
                             push_ending_condition_for_sell_limit_order)

    order.status = AbstractOrder.OrderStatus.FILLED if order.quantity == 0 else (
        AbstractOrder.OrderStatus.PLACED)
    order.save()
    #print('resolve_limit_order', order.status, order.quantity)


def get_depo_by_pk(pk):
    depo = get_object_or_404(Depo, pk=pk)
    return depo


def get_position_by_order(order):
    depo = order.initiator
    symbol = order.symbol
    try:
        return (Position.objects.select_related('depo', 'symbol').
                get(depo=depo, symbol=symbol))
    except ObjectDoesNotExist:
        return None


def get_position_sign(position):
    return 1 if position.quantity > 0 else -1


def get_order_sign(order : AbstractOrder):
    return 1 if AbstractOrder.OrderDirection.BUY else -1


def get_opened_position_equity(depo, symbol):
    pos = get_position_by_order(depo,symbol).filter
    if not pos:
        return 0
    return pos


def request_to_orm_model(request : dict):
    depo = get_depo_by_pk(request['depo_pk'])
    symbol = get_symbol_by_ticker(request['ticker'])
    match [request['order']['dir'], request['order_type']]:
        case ['sell', 'market_order']:
            mo = MarketOrder(quantity=request['order']['quantity'],
                             dir=AbstractOrder.OrderDirection.SELL, symbol=symbol)
            resolve_order(mo)
