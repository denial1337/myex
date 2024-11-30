from ex.models import AbstractOrder, MarketOrder, LimitOrder
#from services.transaction_service import get_position_by_order


def _get_average_price_for_market_order(order):
    # FIXME
    # тут некоторое допущение, я пропущу сложную агрегацию для вычисления
    # средней цены рыночной заявки и просто возьму лучшую цену
    return order.symbol.best_ask if order.dir == AbstractOrder.OrderDirection.BUY \
        else order.symbol.best_bid

def _get_maker_price(order):
    match order:
        case MarketOrder():
            return order.symbol.best_ask if order.dir == AbstractOrder.OrderDirection.BUY \
                else order.symbol.best_bid
        case LimitOrder():
            return order.price
    return None


def _is_valid_market_order(order : MarketOrder):
    if order.initiator.free_equity < order.quantity * _get_average_price_for_market_order(order):
        return False

    maker_orders_count = order.symbol.ask_count \
        if order.dir == AbstractOrder.OrderDirection.BUY else (
        order.symbol.bid_count)

    if order.quantity > maker_orders_count:
        return False

    return True


def _is_valid_limit_order(order : LimitOrder):
    depo = order.initiator
    maker_price = _get_maker_price(order)

    return depo.free_equity > order.quantity * maker_price

def is_valid_order(order):
    match order:
        case LimitOrder():
            return _is_valid_limit_order(order)
        case MarketOrder():
            return _is_valid_market_order(order)
        case _:
            raise ValueError(f'LimitOrder or MarketOrder instance expected but {type(order)} recieved')
