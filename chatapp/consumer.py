import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

# In-memory store for connected users
connected_users = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.message_group_name = f'chat_{self.user_id}_messaging'
        self.chat_group_name = f'chat_{self.user_id}'
        self.subscribed_chats = []

        connected_users[self.user_id] = self.channel_name

        await self.channel_layer.group_add(self.message_group_name, self.channel_name)
        await self.broadcast_online_status()
        await self.accept()

    async def disconnect(self, close_code):
        connected_users.pop(self.user_id, None)

        await self.unsubscribe_from_all_contacts()

        await self.channel_layer.group_discard(self.message_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)

        await self.broadcast_offline_status()

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('action') == 'subscribe':
            chat_ids = data.get('chats_ids', [])
            if chat_ids:
                await self.subscribe_to_chats(chat_ids)
                await self.send(json.dumps({
                    'action': 'subscribed',
                    'message': f'Subscribed to chats {chat_ids}'
                }))
            else:
                await self.send(json.dumps({'error': 'No chats provided for subscription.'}))
            return

        if 'status' in data and 'message_id' in data:
            await self.update_message_status(data['message_id'], data['status'])
            return

        if 'message' in data and 'sender' in data and 'recipient' in data:
            sender = await self.get_user(data['sender'])
            recipient = await self.get_user(data['recipient'])
            message = await self.save_message(sender, recipient, data['message'])

            for user in [recipient, sender]:
                rendered_message = await sync_to_async(render_to_string)(
                    'chatapp/components/message.html',
                    {
                        'messages': [message],
                        'current_user': user,
                    }
                )

                await self.channel_layer.group_send(
                    f'chat_{user.id}_messaging',
                    {
                        'type': 'chat_message',
                        'message_html': rendered_message,
                        'message_id': message.id,
                        'message_text': data['message'],
                        'recipient_id': recipient.id,
                        'sender_id': sender.id,
                        'unread_count': await self.get_unread_count(recipient) if user == recipient else 0,
                    }
                )
            return

        await self.send(json.dumps({'error': 'Invalid data format or missing fields'}))

    # ---------------- Database Access ----------------
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

    # ---------------- WebSocket Handlers ----------------
    async def chat_message(self, event):
        await self.send(json.dumps({
            'message_html': event['message_html'],
            'message_id': event['message_id'],
            'message_text': event['message_text'],
            'sender_id': event['sender_id'],
            'recipient_id': event['recipient_id'],
            'unread_count': event['unread_count'],
        }))

    async def user_status(self, event):
        await self.send(json.dumps({
            'chat_id': event['chat_id'],
            'status': event['status'],
        }))

    # ---------------- Status Broadcasting ----------------
    async def broadcast_online_status(self):
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'user_status',
                'chat_id': self.user_id,
                'status': 'online'
            }
        )

    async def broadcast_offline_status(self):
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'user_status',
                'chat_id': self.user_id,
                'status': 'offline'
            }
        )

    # ---------------- Chat Subscription ----------------
    async def subscribe_to_chats(self, chat_ids):
        for chat in chat_ids:
            chat_group_name = f'chat_{chat.get("chat_id")}'
            self.subscribed_chats.append(chat_group_name)
            await self.channel_layer.group_add(chat_group_name, self.channel_name)

    async def unsubscribe_from_all_contacts(self):
        for chat_group_name in self.subscribed_chats:
            await self.channel_layer.group_discard(chat_group_name, self.channel_name)
