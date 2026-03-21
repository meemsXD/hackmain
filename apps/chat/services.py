from django.utils import timezone
from .models import ChatThread, ChatMessage
from apps.audits.services import audit_log


def ensure_chat_thread(batch):
    thread, _ = ChatThread.objects.get_or_create(batch=batch)
    return thread


def create_system_message(batch, text):
    thread = ensure_chat_thread(batch)
    msg = ChatMessage.objects.create(thread=thread, body=text, is_system=True)
    thread.last_message_at = msg.created_at
    thread.save(update_fields=['last_message_at'])
    return msg


def send_message(batch, user, body):
    thread = ensure_chat_thread(batch)
    msg = ChatMessage.objects.create(thread=thread, author_user=user, body=body, is_system=False)
    thread.last_message_at = msg.created_at
    thread.save(update_fields=['last_message_at'])
    audit_log(user, 'chat_message_sent', 'waste_batch', str(batch.id), None, {'message_id': str(msg.id)})
    return msg
