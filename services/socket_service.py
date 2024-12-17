from channels.layers import get_channel_layer, channel_layers
from asgiref.sync import async_to_sync
# from myex.settings import channel_layers


def send_new_transaction(transaction):
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


def send_order_book_update():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("traders", get_update_order_book_message())


def send_update_depo():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("traders", get_update_depo_message())


def send_update_position():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("traders", get_update_position_message())


def get_update_depo_message():
    return {"type": "depo_update", "message": {"type": "depo_update"}}


def get_update_position_message():
    return {"type": "positions_update", "message": {"type": "positions_update"}}


def get_update_orders_message():
    return {"type": "orders_update", "message": {"type": "orders_update"}}


def get_update_order_book_message():
    return {"type": "order_book", "message": {"type": "order_book_update"}}
