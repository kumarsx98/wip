# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DocumentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.source_name = self.scope['url_route']['kwargs']['source_name']
        self.room_group_name = f'document_updates_{self.source_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'document_update',
                'message': message
            }
        )

    async def document_update(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
