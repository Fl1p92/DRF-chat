from rest_framework import viewsets, mixins

from .models import Chat
from .serializers import ChatSerializer


class ListDestroyChatAPIViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = ChatSerializer

    def get_queryset(self):
        queryset = Chat.objects.filter(owner=self.request.user)
        return queryset
