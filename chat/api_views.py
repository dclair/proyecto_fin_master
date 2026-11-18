import os
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Conversation, Message, ConversationParticipant
from .api_serializers import ConversationSerializer, MessageSerializer

from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import status

User = get_user_model()

class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Devuelve las conversaciones donde el usuario actual es participante
        return Conversation.objects.filter(participants__user=self.request.user).order_by('-created_at')

class ConversationCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        target_user_id = request.data.get('user_id')
        if not target_user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
        if target_user == request.user:
            return Response({'error': 'No puedes chatear contigo mismo'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Buscar conversación 1 a 1 existente
        user_convs = ConversationParticipant.objects.filter(user=request.user).values_list('conversation_id', flat=True)
        target_convs = ConversationParticipant.objects.filter(user=target_user, conversation_id__in=user_convs).values_list('conversation_id', flat=True)
        
        for conv_id in target_convs:
            conv = Conversation.objects.get(id=conv_id)
            if not conv.is_group and conv.participants.count() == 2:
                serializer = ConversationSerializer(conv)
                return Response(serializer.data)
                
        # Crear nueva conversación
        conv = Conversation.objects.create(is_group=False)
        ConversationParticipant.objects.create(conversation=conv, user=request.user)
        ConversationParticipant.objects.create(conversation=conv, user=target_user)
        
        serializer = ConversationSerializer(conv)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        # Validar que el usuario pertenece a la conversación
        if not ConversationParticipant.objects.filter(conversation_id=conversation_id, user=self.request.user).exists():
            return Message.objects.none()
        
        return Message.objects.filter(conversation_id=conversation_id).exclude(hidden_by=self.request.user).order_by('timestamp')

class UnreadMessagesCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        unread_count = 0
        
        # Obtener todas las conversaciones donde el usuario participa
        participants = ConversationParticipant.objects.filter(user=user).select_related('conversation')
        for participant in participants:
            # Contar mensajes posteriores al last_read_timestamp que no hayan sido enviados por el propio usuario
            count = Message.objects.filter(
                conversation=participant.conversation,
                timestamp__gt=participant.last_read_timestamp
            ).exclude(sender=user).exclude(hidden_by=user).count()
            unread_count += count
            
        return Response({'unread_count': unread_count})

from django.utils.timezone import now

class MarkConversationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, conversation_id):
        try:
            participant = ConversationParticipant.objects.get(conversation_id=conversation_id, user=request.user)
            participant.last_read_timestamp = now()
            participant.save()
            return Response({'status': 'ok'})
        except ConversationParticipant.DoesNotExist:
            return Response({'error': 'Not a participant'}, status=status.HTTP_403_FORBIDDEN)

from .api_serializers import UserBasicSerializer, GroupJoinRequestSerializer
from .models import GroupJoinRequest

class GroupConversationCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        name = request.data.get('name')
        user_ids = request.data.get('user_ids', [])
        
        if not name:
            return Response({'error': 'Group name is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not user_ids or not isinstance(user_ids, list):
            return Response({'error': 'user_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Ensure creator is in the group
        if request.user.id not in user_ids:
            user_ids.append(request.user.id)
            
        users = User.objects.filter(id__in=user_ids)
        if users.count() < 2:
            return Response({'error': 'At least 2 users are required to form a group'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Create group conversation
        conv = Conversation.objects.create(is_group=True, name=name, admin=request.user)
        
        # Create participants
        participants = [ConversationParticipant(conversation=conv, user=user) for user in users]
        ConversationParticipant.objects.bulk_create(participants)
        
        serializer = ConversationSerializer(conv)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserListView(generics.ListAPIView):
    serializer_class = UserBasicSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Exclude the current user so they don't select themselves
        return User.objects.exclude(id=self.request.user.id).order_by('first_name', 'username')

class GroupConversationAddUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, conversation_id):
        try:
            conv = Conversation.objects.get(id=conversation_id, is_group=True)
        except Conversation.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
            
        # Verificar que el usuario es el administrador del grupo
        if conv.admin != request.user:
            return Response({'error': 'Only the admin can add users'}, status=status.HTTP_403_FORBIDDEN)
            
        user_ids = request.data.get('user_ids', [])
        if not user_ids or not isinstance(user_ids, list):
            return Response({'error': 'user_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)
            
        users = User.objects.filter(id__in=user_ids)
        
        # Filtrar los que ya existen
        existing_ids = set(ConversationParticipant.objects.filter(conversation=conv).values_list('user_id', flat=True))
        
        new_participants = []
        for u in users:
            if u.id not in existing_ids:
                new_participants.append(ConversationParticipant(conversation=conv, user=u))
                
        if new_participants:
            ConversationParticipant.objects.bulk_create(new_participants)
            
        return Response({'status': 'ok', 'added': len(new_participants)})

class DiscoverGroupsView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Grupos donde NO participo
        my_group_ids = ConversationParticipant.objects.filter(
            user=self.request.user, conversation__is_group=True
        ).values_list('conversation_id', flat=True)
        return Conversation.objects.filter(is_group=True).exclude(id__in=my_group_ids)

class RequestJoinGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, conversation_id):
        try:
            conv = Conversation.objects.get(id=conversation_id, is_group=True)
        except Conversation.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
            
        # Check if already a participant
        if ConversationParticipant.objects.filter(conversation=conv, user=request.user).exists():
            return Response({'error': 'Already a participant'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get or create pending request
        join_req, created = GroupJoinRequest.objects.get_or_create(
            conversation=conv,
            user=request.user,
            defaults={'status': 'pending'}
        )
        if not created and join_req.status != 'pending':
            join_req.status = 'pending'
            join_req.save()
            
        return Response({'status': 'ok'})

class GroupJoinRequestsListView(generics.ListAPIView):
    serializer_class = GroupJoinRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Solicitudes pendientes para los grupos que administro
        return GroupJoinRequest.objects.filter(
            conversation__admin=self.request.user,
            status='pending'
        )

class ManageJoinRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        try:
            join_req = GroupJoinRequest.objects.get(id=request_id, conversation__admin=request.user)
        except GroupJoinRequest.DoesNotExist:
            return Response({'error': 'Request not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)
            
        action = request.data.get('action')
        if action not in ['accept', 'reject']:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
            
        if action == 'accept':
            join_req.status = 'accepted'
            ConversationParticipant.objects.get_or_create(conversation=join_req.conversation, user=join_req.user)
        else:
            join_req.status = 'rejected'
            
        join_req.save()
        return Response({'status': 'ok'})

class ConversationDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, conversation_id):
        try:
            conv = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        if conv.is_group:
            if conv.admin != request.user:
                return Response({'error': 'Only the group administrator can delete this group'}, status=status.HTTP_403_FORBIDDEN)
        else:
            if not ConversationParticipant.objects.filter(conversation=conv, user=request.user).exists():
                return Response({'error': 'You are not a participant in this conversation'}, status=status.HTTP_403_FORBIDDEN)

        # Delete physical files from all messages in the conversation to prevent storage leaks
        for msg in conv.messages.exclude(attachment=''):
            if msg.attachment:
                msg.attachment.delete(save=False)

        conv.delete()
        return Response({'status': 'ok'})

import io
import mimetypes
from django.conf import settings
from django.http import HttpResponse, Http404, FileResponse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

def validate_file_magic_bytes(file_obj, attachment_type):
    """
    Valida las firmas de bytes (magic numbers) para asegurar que el contenido
    coincide con el tipo de archivo declarado y no es un ejecutable disfrazado.
    """
    pos = file_obj.tell()
    header = file_obj.read(32)
    file_obj.seek(pos)

    if not header:
        return False

    if attachment_type == 'image':
        if header.startswith(b'\xff\xd8\xff'):
            return True
        if header.startswith(b'\x89PNG\r\n\x1a\n'):
            return True
        if header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
            return True
        if header.startswith(b'RIFF') and len(header) >= 12 and header[8:12] == b'WEBP':
            return True
        return False

    elif attachment_type == 'document':
        if header.startswith(b'%PDF-'):
            return True
        if header.startswith(b'PK\x03\x04'):
            return True
        if header.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
            return True
        ext = os.path.splitext(file_obj.name)[1].lower()
        if ext == '.txt' and b'\x00' not in header:
            return True
        return False

    elif attachment_type == 'video':
        if len(header) >= 8 and header[4:8] in (b'ftyp', b'moov', b'wide'):
            return True
        if header.startswith(b'\x1a\x45\xdf\xa3'):
            return True
        return False

    elif attachment_type == 'audio':
        if header.startswith(b'ID3') or (len(header) >= 2 and header[0] == 0xff and (header[1] & 0xe0) == 0xe0):
            return True
        if header.startswith(b'RIFF') and len(header) >= 12 and header[8:12] == b'WAVE':
            return True
        if header.startswith(b'OggS'):
            return True
        if len(header) >= 8 and header[4:8] == b'ftyp':
            return True
        if header.startswith(b'\x1a\x45\xdf\xa3'):
            return True
        return False

    return False

def sanitize_and_reencode_image(file_obj):
    """
    Abre la imagen con Pillow, verifica su integridad y la re-codifica
    limpiando metadatos EXIF, coordenadas GPS y posibles payloads políglotas.
    """
    pos = file_obj.tell()
    try:
        file_obj.seek(0)
        with Image.open(file_obj) as img:
            img.verify()

        file_obj.seek(0)
        with Image.open(file_obj) as img:
            fmt = img.format
            if fmt not in ['JPEG', 'PNG', 'WEBP', 'GIF']:
                raise ValueError(f"Formato de imagen no permitido: {fmt}")

            output_io = io.BytesIO()

            if fmt == 'GIF' and getattr(img, 'is_animated', False):
                img.save(output_io, format='GIF', save_all=True)
                out_ext = '.gif'
                out_mime = 'image/gif'
            elif img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                clean_img = Image.new('RGBA', img.size)
                clean_img.paste(img, (0, 0))
                clean_img.save(output_io, format='PNG', optimize=True)
                out_ext = '.png'
                out_mime = 'image/png'
            else:
                clean_img = Image.new('RGB', img.size)
                clean_img.paste(img, (0, 0))
                clean_img.save(output_io, format='JPEG', quality=85, optimize=True)
                out_ext = '.jpg'
                out_mime = 'image/jpeg'

            output_io.seek(0)
            base_name = os.path.splitext(file_obj.name)[0]
            sanitized_file = SimpleUploadedFile(
                name=f"{base_name}{out_ext}",
                content=output_io.getvalue(),
                content_type=out_mime
            )
            return sanitized_file
    except Exception as e:
        raise ValueError(f"Imagen inválida o corrupta: {e}")
    finally:
        file_obj.seek(pos)

from rest_framework.parsers import MultiPartParser, FormParser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class MessageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, conversation_id):
        try:
            conv = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        if not ConversationParticipant.objects.filter(conversation=conv, user=request.user).exists():
            return Response({'error': 'You are not a participant in this conversation'}, status=status.HTTP_403_FORBIDDEN)

        file_obj = request.FILES.get('file')
        content = request.data.get('content', '').strip()
        
        if not file_obj and not content:
            return Response({'error': 'Either file or content is required'}, status=status.HTTP_400_BAD_REQUEST)

        attachment_type = None
        ALLOWED_IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        ALLOWED_VIDEO_EXTS = {'.mp4', '.webm', '.mov'}
        ALLOWED_AUDIO_EXTS = {'.mp3', '.wav', '.ogg', '.webm', '.m4a'}
        ALLOWED_DOCUMENT_EXTS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.odt', '.ods', '.zip'}

        if file_obj:
            ext = os.path.splitext(file_obj.name)[1].lower()
            mime_type = getattr(file_obj, 'content_type', '') or ''
            file_size = file_obj.size
            
            MB = 1024 * 1024
            if mime_type.startswith('image/') and ext in ALLOWED_IMAGE_EXTS:
                attachment_type = 'image'
                if file_size > 5 * MB:
                    return Response({'error': 'Image file size exceeds 5MB limit'}, status=status.HTTP_400_BAD_REQUEST)
            elif mime_type.startswith('video/') and ext in ALLOWED_VIDEO_EXTS:
                attachment_type = 'video'
                if file_size > 15 * MB:
                    return Response({'error': 'Video file size exceeds 15MB limit'}, status=status.HTTP_400_BAD_REQUEST)
            elif (mime_type.startswith('audio/') or mime_type in ('video/webm', 'audio/webm')) and ext in ALLOWED_AUDIO_EXTS:
                attachment_type = 'audio'
                if file_size > 10 * MB:
                    return Response({'error': 'Audio file size exceeds 10MB limit'}, status=status.HTTP_400_BAD_REQUEST)
            elif ext in ALLOWED_DOCUMENT_EXTS:
                attachment_type = 'document'
                if file_size > 5 * MB:
                    return Response({'error': 'Document file size exceeds 5MB limit'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {'error': f'Tipo de archivo no permitido ({ext}). Formatos permitidos: imágenes (jpg, png, webp, gif), audio (mp3, wav, ogg, webm), video (mp4, webm) y documentos (pdf, doc, docx, xls, xlsx, txt, zip).'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validar firmas de bytes reales (magic bytes)
            if not validate_file_magic_bytes(file_obj, attachment_type):
                return Response(
                    {'error': f'Contenido de archivo no válido para el tipo {attachment_type} (firma de bytes errónea).'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Re-codificar imágenes con Pillow y eliminar metadatos EXIF
            if attachment_type == 'image':
                try:
                    file_obj = sanitize_and_reencode_image(file_obj)
                except ValueError as err:
                    return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el mensaje
        msg = Message.objects.create(
            conversation=conv,
            sender=request.user,
            content=content if content else None,
            attachment=file_obj,
            attachment_type=attachment_type
        )
        
        # Actualizar timestamp para nosotros
        ConversationParticipant.objects.filter(conversation=conv, user=request.user).update(last_read_timestamp=now())

        serializer = MessageSerializer(msg)
        message_data = serializer.data

        # Broadcast via Channels
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{conversation_id}'
        
        # Make absolute URL for the attachment if it exists
        if msg.attachment:
            from django.urls import reverse
            message_data['attachment'] = request.build_absolute_uri(
                reverse('api-message-attachment', kwargs={'message_id': msg.id})
            )

        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'chat_message',
                'full_message': message_data
            }
        )

        return Response(message_data, status=status.HTTP_201_CREATED)

class MessageDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, message_id):
        try:
            msg = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

        if msg.sender != request.user:
            return Response({'error': 'You can only delete your own messages'}, status=status.HTTP_403_FORBIDDEN)

        # Broadcast deletion via Channels before deleting from DB
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{msg.conversation_id}'
        
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'message_deleted',
                'message_id': msg.id
            }
        )

        # Delete physical file if exists
        if msg.attachment:
            msg.attachment.delete(save=False)
            
        msg.delete()
        
        return Response({'status': 'deleted'})

class MessageHideView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, message_id):
        try:
            msg = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is a participant of the conversation
        if not ConversationParticipant.objects.filter(conversation=msg.conversation, user=request.user).exists():
            return Response({'error': 'You are not a participant in this conversation'}, status=status.HTTP_403_FORBIDDEN)

        msg.hidden_by.add(request.user)
        return Response({'status': 'hidden'})

class ProtectedAttachmentDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, message_id):
        try:
            msg = Message.objects.select_related('conversation').get(id=message_id)
        except Message.DoesNotExist:
            raise Http404("Mensaje no encontrado")

        if not msg.attachment:
            raise Http404("El mensaje no tiene archivos adjuntos")

        # Validar que el usuario sea participante de la conversación o superusuario
        if not ConversationParticipant.objects.filter(conversation=msg.conversation, user=request.user).exists() and not request.user.is_superuser:
            return Response({'error': 'No tienes permiso para acceder a este archivo privado'}, status=status.HTTP_403_FORBIDDEN)

        file_path = msg.attachment.name  # ej: 'chat_attachments/informe.pdf'
        filename = os.path.basename(file_path)
        content_type, _ = mimetypes.guess_type(filename)
        content_type = content_type or 'application/octet-stream'

        # En producción (Nginx con X-Accel-Redirect)
        if not settings.DEBUG:
            response = HttpResponse()
            response['X-Accel-Redirect'] = f'/protected_media/{file_path}'
            response['Content-Type'] = content_type
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response

        # En desarrollo o pruebas (servir con FileResponse de Django)
        full_disk_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if not os.path.exists(full_disk_path):
            raise Http404("El archivo no se encuentra en el servidor")

        return FileResponse(open(full_disk_path, 'rb'), content_type=content_type)
