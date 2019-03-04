from django.contrib.auth.models import User

from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ContactLine, BlackList, BlackListLine
from .permissions import IsOwner
from .serializers import UserSerializer, ContactLineSerializer, PasswordChangeSerializer
from apps.chats.models import Chat


class UserAPIViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'password_change':
            return PasswordChangeSerializer
        else:
            return UserSerializer

    @action(methods=['put'], detail=True, permission_classes=[IsOwner],
            url_path='change-password', url_name='password-change')
    def password_change(self, request, format=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='check-user-exists', url_name='check-exists')
    def check_exists(self, request, format=None, *args, **kwargs):
        username = self.request.query_params.get('username')
        if username:
            if User.objects.filter(username=username).exists():
                return Response({"detail": f"'{username}' exists."},
                                status=status.HTTP_200_OK)
            else:
                return Response({"detail": f"'{username}' does not exists."},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "The 'username' get parameter is not provided."},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='block', url_name='block')
    def user_block(self, request, format=None, *args, **kwargs):
        owner = request.user
        try:
            blocked_user = User.objects.get(pk=self.kwargs['pk'])
        except User.DoesNotExist:
            return Response({"detail": f"User 'pk' {self.kwargs['pk']} is invalid."},
                            status=status.HTTP_400_BAD_REQUEST)

        owner_black_list, _ = BlackList.objects.get_or_create(owner=owner)
        line, created = BlackListLine.objects.get_or_create(blacklist=owner_black_list, blocked_contact=blocked_user)
        if created:
            if owner.contacts_list.contact_lines.filter(contact=blocked_user).exists():
                owner.contacts_list.contact_lines.filter(contact=blocked_user).delete()
            return Response({"detail": f"{line.blocked_contact} is blocked."},
                            status=status.HTTP_200_OK)
        else:
            return Response({"detail": f"{line.blocked_contact} is already blocked."},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='unblock', url_name='unblock')
    def user_unblock(self, request, format=None, *args, **kwargs):
        try:
            instance = BlackListLine.objects.get(
                blacklist__owner=request.user,
                blocked_contact__pk=self.kwargs['pk'],
            )

            instance.delete()
            return Response({"detail": f"{instance.blocked_contact.username} is unblocked."},
                            status=status.HTTP_200_OK)

        except BlackListLine.DoesNotExist:
            return Response({"detail": f"Blocked user#{self.kwargs['pk']} does not exists."},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='create-chat', url_name='create-chat')
    def create_chat(self, request, format=None, *args, **kwargs):
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
            return Response({"detail": f"Chat with {user} is created. ID # {chat.id}."},
                            status=status.HTTP_201_CREATED)


class CreateDestroyListContactsAPIViewSet(mixins.CreateModelMixin,
                                          mixins.DestroyModelMixin,
                                          mixins.ListModelMixin,
                                          viewsets.GenericViewSet):
    serializer_class = ContactLineSerializer

    def get_queryset(self):
        queryset = ContactLine.objects.filter(contacts_list__owner=self.request.user).prefetch_related('contact')
        return queryset
