import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.decorators import login_required


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('YEEEES')
        self.user = self.scope['user']
        if self.user.is_authenticated:

            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Логика отключения
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Обработка полученных данных
        await self.send(text_data=json.dumps({
            'message': 'Hello, authenticated user!'
        }))