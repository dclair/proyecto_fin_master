import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, ConversationParticipant, Message
from django.contrib.auth.models import User
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_user_auth(self):
        user = self.scope["user"]
        return user.is_authenticated, getattr(user, 'id', None), getattr(user, 'username', None)

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f"chat_{self.conversation_id}"

        # Resolver el usuario de forma segura (evita SynchronousOnlyOperation)
        is_authenticated, self.user_id, self.username = await self.get_user_auth()

        # Rechazar si no está autenticado
        if not is_authenticated:
            await self.close()
            return
            
        # Verificar que el usuario pertenece a la conversación
        is_participant = await self.is_participant(self.user_id, self.conversation_id)
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
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            if not isinstance(message, str):
                await self.send(text_data=json.dumps({'error': 'El mensaje debe ser una cadena de texto'}))
                return
            message = message.strip()
        except (json.JSONDecodeError, AttributeError):
            await self.send(text_data=json.dumps({'error': 'Formato JSON inválido'}))
            return

        if not message:
            await self.send(text_data=json.dumps({'error': 'El mensaje no puede estar vacío'}))
            return

        if len(message) > 4000:
            await self.send(text_data=json.dumps({'error': 'El mensaje excede el límite máximo de 4000 caracteres'}))
            return

        # Re-verificar que sigue siendo participante activo antes de despachar
        is_participant = await self.is_participant(self.user_id, self.conversation_id)
        if not is_participant:
            await self.send(text_data=json.dumps({'error': 'No eres participante de esta conversación'}))
            await self.close()
            return

        # Guardar en DB
        new_msg = await self.save_message(self.user_id, self.conversation_id, message)
        await self.update_last_read(self.user_id, self.conversation_id)

        # Enviar el mensaje al grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': new_msg.content,
                'sender': self.username,
                'message_id': new_msg.id,
                'timestamp': str(new_msg.timestamp)
            }
        )

    # Recibir mensaje desde el grupo de Channels
    async def chat_message(self, event):
        # Enviar el mensaje por el WebSocket al cliente final
        if 'full_message' in event:
            await self.send(text_data=json.dumps(event['full_message']))
        else:
            payload = {
                'message': event['message'],
                'sender': event['sender'],
                'message_id': event['message_id'],
                'timestamp': event['timestamp']
            }
            if 'attachment' in event:
                payload['attachment'] = event['attachment']
            if 'attachment_name' in event:
                payload['attachment_name'] = event['attachment_name']
            if 'attachment_type' in event:
                payload['attachment_type'] = event['attachment_type']
            await self.send(text_data=json.dumps(payload))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'action': 'delete',
            'message_id': event['message_id']
        }))

    @database_sync_to_async
    def is_participant(self, user_id, conversation_id):
        return ConversationParticipant.objects.filter(user_id=user_id, conversation_id=conversation_id).exists()

    @database_sync_to_async
    def save_message(self, user_id, conversation_id, content):
        return Message.objects.create(
            sender_id=user_id,
            conversation_id=conversation_id,
            content=content
        )

    @database_sync_to_async
    def update_last_read(self, user_id, conversation_id):
        ConversationParticipant.objects.filter(
            user_id=user_id, conversation_id=conversation_id
        ).update(last_read_timestamp=timezone.now())
