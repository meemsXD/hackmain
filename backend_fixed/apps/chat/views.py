from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.batches.models import WasteBatch
from apps.access.permissions import has_driver_access_to_batch
from .models import ChatMessage
from .serializers import ChatMessageSerializer, SendMessageSerializer
from .services import send_message


def can_access_chat(user, batch):
    return (
        user.is_superuser
        or user.user_roles.filter(role__in=['INSPECTOR', 'ADMIN']).exists()
        or batch.creator_org_id == user.organization_id
        or batch.processor_org_id == user.organization_id
        or has_driver_access_to_batch(user, batch)
    )

class ChatMessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        batch = get_object_or_404(WasteBatch, pk=self.kwargs['batch_id'])
        if not can_access_chat(self.request.user, batch):
            return ChatMessage.objects.none()
        return batch.chat_thread.messages.select_related('author_user') if hasattr(batch, 'chat_thread') else ChatMessage.objects.none()

class ChatMessageCreateView(APIView):
    def post(self, request, batch_id):
        batch = get_object_or_404(WasteBatch, pk=batch_id)
        if not can_access_chat(request.user, batch):
            return Response({'detail': 'Нет доступа к чату'}, status=403)
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        msg = send_message(batch=batch, user=request.user, body=serializer.validated_data['body'])
        return Response(ChatMessageSerializer(msg).data, status=201)
