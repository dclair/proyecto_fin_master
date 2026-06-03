from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Conversation {self.id} (Group: {self.is_group})"

class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('conversation', 'user')
        
    def __str__(self):
        return f"{self.user.username} in Conv {self.conversation.id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Msg {self.id} by {self.sender.username} in Conv {self.conversation.id}"
