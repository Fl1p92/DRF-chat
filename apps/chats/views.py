from django.contrib.auth.models import User

from rest_framework import generics, status, views
from rest_framework.response import Response

from .models import Chat
from .serializers import ChatSerializer


class CreateChatAPIView(views.APIView):

    def post(self, request, *args, **kwargs):
        owner = request.user
        try:
            user = User.objects.get(pk=self.kwargs['pk'])
        except User.DoesNotExist:
            return Response({"detail": f"User 'pk' {self.kwargs['pk']} is invalid."},
                            status=status.HTTP_400_BAD_REQUEST)
        if Chat.objects.filter(owner=owner, users=user).exists():
            return Response({"detail": f"Chat with {user} is already exists."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            chat = Chat.objects.create(owner=owner)
            chat.users.add(owner, user)
            return Response({"detail": f"Chat with {user} is created. ID # {chat.id}"},
                            status=status.HTTP_201_CREATED)


class ListChatAPIView(generics.ListAPIView):
    serializer_class = ChatSerializer

    def get_queryset(self):
        queryset = Chat.objects.filter(owner=self.request.user)
        return queryset
