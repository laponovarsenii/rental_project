from django.urls import path
from .views import ChatCreateView, MessageCreateView, ChatMessagesListView

urlpatterns = [
    path('create/', ChatCreateView.as_view(), name='chat-create'),
    path('message/', MessageCreateView.as_view(), name='chat-message'),
    path('<int:chat_id>/messages/', ChatMessagesListView.as_view(), name='chat-messages'),
]