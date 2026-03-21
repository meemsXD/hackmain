from django.urls import path
from .views import ChatMessageListView, ChatMessageCreateView

urlpatterns = [
    path('batches/<uuid:batch_id>/chat/messages', ChatMessageListView.as_view(), name='chat-messages'),
    path('batches/<uuid:batch_id>/chat/messages/send', ChatMessageCreateView.as_view(), name='chat-messages-send'),
]
