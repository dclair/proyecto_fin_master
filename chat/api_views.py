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
