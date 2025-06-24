import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from directs.models import Message
from channels.db import database_sync_to_async

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
        print("WebSocket receive called")
        try:
            data = json.loads(text_data)
            message = data['message']
            from_username = data['username']
            profile_image = data.get('profile_image', '')

            # Determine the recipient's username from the room name
            room_name_parts = self.room_name.split('_')
            to_username = None
            if room_name_parts[0] == from_username:
                to_username = room_name_parts[1]
            else:
                to_username = room_name_parts[0]

            print(f"Received message: {message} from: {from_username} to: {to_username}")

            # Call the async helper to save the message
            if to_username:
                await self.save_message(from_username, to_username, message)
            else:
                print("Error: Could not determine recipient.")

            # Broadcast the message to the room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': from_username,
                    'profile_image': profile_image,
                }
            )
        except Exception as e:
            print(f"Error in receive method: {e}")

    @database_sync_to_async
    def save_message(self, from_username, to_username, message_body):
        from_user = User.objects.get(username=from_username)
        to_user = User.objects.get(username=to_username)
        Message.sender_message(from_user, to_user, message_body)
        print("Message saved to DB")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'profile_image': event['profile_image'],
        }))