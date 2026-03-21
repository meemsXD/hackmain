from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'author_name', 'author_user', 'body', 'is_system', 'created_at']
        read_only_fields = ['id', 'author_name', 'author_user', 'is_system', 'created_at']

    def get_author_name(self, obj):
        return obj.author_user.full_name if obj.author_user else 'Система'

class SendMessageSerializer(serializers.Serializer):
    body = serializers.CharField(max_length=2000)
