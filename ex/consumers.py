import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from services.DTO_service import socket_message_to_order
from services.socket_service import (
    get_update_orders_message,
    get_update_position_message,
    send_order_book_update,
    get_update_depo_message,
)
from services.transaction_service import resolve_order, close_order


class MyConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_add)("traders", self.channel_name)
            self.accept()
            self.send(text_data=json.dumps({"status": "ok"}))
        else:
            self.close()

    def receive(self, text_data: str | None = None, bytes_data: None = None) -> None:
        data = json.loads(text_data)
        self.send(
            text_data=json.dumps(
                {"type": "just_message", "message": "Data processed successfully!"}
            )
        )
        try:
            if data["type"] == "new_order":
                order = socket_message_to_order(data)
                resolve_order(order)
            if data["type"] == "close_order":
                if close_order(data["order_pk"]):
                    send_order_book_update()

            self.send(text_data=json.dumps(get_update_depo_message()))
            self.send(text_data=json.dumps(get_update_position_message()))
            self.send(text_data=json.dumps(get_update_orders_message()))
        except ValueError as e:
            print(e)

    def disconnect(self, close_code):
        self.channel_layer.group_discard("traders", self.channel_name)

    def transaction(self, event):
        self.send(text_data=json.dumps(event["message"]))

    def order_book(self, event):
        self.send(text_data=json.dumps(event["message"]))
