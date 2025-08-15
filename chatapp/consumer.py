from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import json

connected_users = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Import models here, after Django is ready
        from authapp.models import CustomUser
        from chatapp.models import Message

        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.message_group_name = f'chat_{self.user_id}_messaging'
        self.chat_group_name = f'chat_{self.user_id}'
        self.subscribed_chats = []

        connected_users[self.user_id] = self.channel_name

        await self.channel_layer.group_add(self.message_group_name, self.channel_name)
        await self.broadcast_online_status()
        await self.accept()

    @database_sync_to_async
    def get_user(self, user_id):
        from authapp.models import CustomUser
        return CustomUser.objects.get(id=user_id)

    @database_sync_to_async
    def save_message(self, sender, recipient, message_text):
        from chatapp.models import Message
        return Message.objects.create(sender=sender, recipient=recipient, message=message_text, status='sent')

    @database_sync_to_async
    def update_message_status(self, message_id, status):
        from chatapp.models import Message
        message = Message.objects.get(id=message_id)
        message.status = status
        message.save()

    @database_sync_to_async
    def get_unread_count(self, recipient):
        from chatapp.models import Message
        return Message.objects.filter(recipient=recipient, status='delivered').count()
