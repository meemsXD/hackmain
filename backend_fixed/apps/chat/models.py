from django.db import models
from apps.common.models import BaseModel

class ChatThread(BaseModel):
    batch = models.OneToOneField('batches.WasteBatch', on_delete=models.CASCADE, related_name='chat_thread')
    last_message_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Thread {self.batch.batch_number}'

class ChatMessage(BaseModel):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='messages')
    author_user = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='chat_messages')
    body = models.TextField()
    is_system = models.BooleanField(default=False)

    class Meta:
        ordering = ('created_at',)
