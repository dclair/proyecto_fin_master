from django.urls import path
from . import api_views

urlpatterns = [
    path('conversations/', api_views.ConversationListView.as_view(), name='api-conversations'),
    path('conversations/create/', api_views.ConversationCreateView.as_view(), name='api-conversations-create'),
    path('conversations/<int:conversation_id>/messages/', api_views.MessageListView.as_view(), name='api-messages'),
    path('conversations/<int:conversation_id>/read/', api_views.MarkConversationReadView.as_view(), name='api-conversations-read'),
    path('unread_count/', api_views.UnreadMessagesCountView.as_view(), name='api-unread-count'),
]
