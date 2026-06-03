import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, ConversationParticipant, Message
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f"chat_{self.conversation_id}"

        # Rechazar si no está autenticado
        if not self.user.is_authenticated:
            await self.close()
            return
            
        # Verificar que el usuario pertenece a la conversación
        is_participant = await self.is_participant(self.user, self.conversation_id)
        if not is_participant:
            await self.close()
            return

        # Unirse a la sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Abandonar la sala
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recibir mensaje desde el WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Guardar en DB
        new_msg = await self.save_message(self.user, self.conversation_id, message)

        # Enviar el mensaje al grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': new_msg.content,
                'sender': self.user.username,
                'message_id': new_msg.id,
                'timestamp': str(new_msg.timestamp)
            }
        )

    # Recibir mensaje desde el grupo de Channels
    async def chat_message(self, event):
        # Enviar el mensaje por el WebSocket al cliente final
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def is_participant(self, user, conversation_id):
        return ConversationParticipant.objects.filter(user=user, conversation_id=conversation_id).exists()

    @database_sync_to_async
    def save_message(self, user, conversation_id, content):
        return Message.objects.create(
            sender=user,
            conversation_id=conversation_id,
            content=content
        )
