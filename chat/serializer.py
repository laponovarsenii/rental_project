from rest_framework import serializers
from chat.models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id',
            'chat',
            'sender',
            'text',
            'sent_at',
        ]
        read_only_fields = [
            'id',
            'sender',
            'sent_at',
        ]

class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = [
            'id',
            'listing',
            'user',
            'owner',
            'created_at',
            'messages',
        ]