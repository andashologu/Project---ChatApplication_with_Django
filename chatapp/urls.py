from django.urls import path
from . import views
from .views import chats_view
from .views import chat_messages_view

urlpatterns = [
    path("", views.index, name="chat"),
    path('chats/', chats_view, name='chats_view'),
    path('chat/<int:contact_id>/', chat_messages_view, name='chat_messages_view'),
]