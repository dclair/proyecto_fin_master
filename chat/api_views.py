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
        
        return Message.objects.filter(conversation_id=conversation_id).order_by('timestamp')

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
            ).exclude(sender=user).count()
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

        conv.delete()
        return Response({'status': 'ok'})
