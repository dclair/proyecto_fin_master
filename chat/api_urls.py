from django.urls import path
from . import api_views

urlpatterns = [
    path('conversations/', api_views.ConversationListView.as_view(), name='api-conversations'),
    path('conversations/create/', api_views.ConversationCreateView.as_view(), name='api-conversations-create'),
    path('groups/create/', api_views.GroupConversationCreateView.as_view(), name='api-groups-create'),
    path('groups/discover/', api_views.DiscoverGroupsView.as_view(), name='api-groups-discover'),
    path('groups/<int:conversation_id>/add_users/', api_views.GroupConversationAddUserView.as_view(), name='api-groups-add-users'),
    path('groups/<int:conversation_id>/request_join/', api_views.RequestJoinGroupView.as_view(), name='api-groups-request-join'),
    path('groups/join_requests/', api_views.GroupJoinRequestsListView.as_view(), name='api-groups-join-requests'),
    path('groups/join_requests/<int:request_id>/manage/', api_views.ManageJoinRequestView.as_view(), name='api-groups-manage-request'),
    path('conversations/<int:conversation_id>/delete/', api_views.ConversationDeleteView.as_view(), name='api-conversations-delete'),
    path('conversations/<int:conversation_id>/messages/', api_views.MessageListView.as_view(), name='api-messages'),
    path('conversations/<int:conversation_id>/upload/', api_views.MessageUploadView.as_view(), name='api-messages-upload'),
    path('conversations/<int:conversation_id>/read/', api_views.MarkConversationReadView.as_view(), name='api-conversations-read'),
    path('messages/<int:message_id>/delete/', api_views.MessageDeleteView.as_view(), name='api-messages-delete'),
    path('messages/<int:message_id>/hide/', api_views.MessageHideView.as_view(), name='api-messages-hide'),
    path('unread_count/', api_views.UnreadMessagesCountView.as_view(), name='api-unread-count'),
    path('users/', api_views.UserListView.as_view(), name='api-chat-users'),
]
