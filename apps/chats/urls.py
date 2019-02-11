from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = format_suffix_patterns([
    path('users/<int:pk>/create-chat/', views.CreateChatAPIView.as_view(), name='chat-create'),
    path('chats/', views.ListChatAPIView.as_view(), name='chat-list'),
    path('chats/<int:pk>/', views.DestroyChatAPIView.as_view(), name='chat-destroy'),
])
