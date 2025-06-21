import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from directs.models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
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
        data = json.loads(text_data)
        message = data['message']
        sender_username = data['sender']
        to_user_username = self.room_name
        sender = await sync_to_async(User.objects.get)(username=sender_username)
        to_user = await sync_to_async(User.objects.get)(username=to_user_username)
        await sync_to_async(Message.sender_message)(sender, to_user, message)
        async def chat_message(self, event):
            message = event['message']
            sender = event['sender']
            await self.send(text_data=json.dumps({
        'message': message,
        'sender': sender,
    }))

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        })) 
        
