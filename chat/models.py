from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    is_group = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='administered_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.is_group and self.name:
            return f"Conversation {self.id} (Group: {self.name})"
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
    content = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    attachment_type = models.CharField(max_length=20, blank=True, null=True) # 'image', 'video', 'document'
    timestamp = models.DateTimeField(auto_now_add=True)
    hidden_by = models.ManyToManyField(User, related_name='hidden_messages', blank=True)
    
    def __str__(self):
        return f"Msg {self.id} by {self.sender.username} in Conv {self.conversation.id}"

    @property
    def attachment_name(self):
        if not self.attachment:
            return None
        import os
        import re
        name = os.path.basename(self.attachment.name)
        root, ext = os.path.splitext(name)
        match = re.search(r'_([a-zA-Z0-9]{7})$', root)
        if match:
            suffix = match.group(1)
            has_upper = any(c.isupper() for c in suffix)
            has_lower = any(c.islower() for c in suffix)
            has_digit = any(c.isdigit() for c in suffix)
            if (has_upper and has_lower) or (has_digit and (has_upper or has_lower)):
                cleaned_root = root[:-8]
                if cleaned_root:
                    return f"{cleaned_root}{ext}"
        return name

class GroupJoinRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='join_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_join_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('conversation', 'user')

    def __str__(self):
        return f"{self.user.username} -> {self.conversation.name} ({self.status})"
