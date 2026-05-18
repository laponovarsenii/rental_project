from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Chat, Message
from .serializer import ChatSerializer, MessageSerializer
from listings.models import Listing

class ChatCreateView(generics.CreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        listing_id = request.data.get('listing')
        listing = Listing.objects.get(id=listing_id)
        owner = listing.owner
        user = request.user

        if user == owner:
            raise PermissionDenied("You can't start a chat with yourself.")

        chat, created = Chat.objects.get_or_create(
            listing=listing,
            user=user,
            owner=owner
        )
        serializer = self.get_serializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        chat_id = self.request.data.get('chat')
        if not chat_id:
            raise PermissionDenied("Chat is required.")
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            raise PermissionDenied("The chat does not exist.")
        user = self.request.user
        if user != chat.user and user != chat.owner:
            raise PermissionDenied("You do not have access to this chat.")
        serializer.save(sender=user, chat=chat)


class ChatMessagesListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        user = self.request.user
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            raise PermissionDenied("Chat not found.")
        if user != chat.user and user != chat.owner:
            raise PermissionDenied("You do not have access to this chat.")
        return Message.objects.filter(chat=chat).order_by('sent_at')



