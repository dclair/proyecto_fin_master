from rest_framework import serializers
from .models import Conversation, ConversationParticipant, Message, GroupJoinRequest
from django.contrib.auth.models import User
from django.contrib.auth.models import User

class UserBasicSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture_url']
        
    def get_profile_picture_url(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.profile_picture_url
        return "/media/profile_pictures/default_profile.png"

class MessageSerializer(serializers.ModelSerializer):
    sender = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'attachment', 'attachment_type', 'timestamp']

class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'is_group', 'name', 'admin', 'created_at', 'participants', 'last_message', 'unread_count']
        
    def get_participants(self, obj):
        # Obtener los usuarios de los participantes
        users = [p.user for p in obj.participants.select_related('user', 'user__profile').all()]
        return UserBasicSerializer(users, many=True).data
        
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        participant = obj.participants.filter(user=request.user).first()
        if not participant:
            return 0
        return obj.messages.filter(timestamp__gt=participant.last_read_timestamp).count()

class GroupJoinRequestSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    conversation_name = serializers.CharField(source='conversation.name', read_only=True)
    
    class Meta:
        model = GroupJoinRequest
        fields = ['id', 'conversation', 'conversation_name', 'user', 'status', 'created_at']
