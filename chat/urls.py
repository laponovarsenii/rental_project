from django.urls import path
from .views import ChatCreateView, MessageCreateView, ChatMessagesListView

urlpatterns = [
    path('chat/create/', ChatCreateView.as_view()),
    path('chat/message/', MessageCreateView.as_view()),
    path('chat/<int:chat_id>/messages/', ChatMessagesListView.as_view()),
]