from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ex.models import Transaction


def send_new_transaction(transaction: Transaction) -> None:
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "traders",
        {
            "type": "transaction",
            "message": {
                "type": "update_data",
                "price": transaction.price,
                "datetime": transaction.datetime.strftime("%H:%M:%S %m.%d"),
            },
        },
    )
    send_order_book_update()


def send_order_book_update() -> None:
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("traders", get_update_order_book_message())


def send_update_depo() -> None:
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("traders", get_update_depo_message())


def send_update_position() -> None:
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("traders", get_update_position_message())


def get_update_depo_message() -> dict:
    return {"type": "depo_update", "message": {"type": "depo_update"}}


def get_update_position_message() -> dict:
    return {"type": "positions_update", "message": {"type": "positions_update"}}


def get_update_orders_message() -> dict:
    return {"type": "orders_update", "message": {"type": "orders_update"}}


def get_update_order_book_message() -> dict:
    return {"type": "order_book", "message": {"type": "order_book_update"}}
