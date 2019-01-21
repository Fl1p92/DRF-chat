from django.contrib.auth.models import User

from rest_framework import generics, permissions, status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import ContactLine, BlackList, BlackListLine
from .permissions import IsOwner
from .serializers import UserSerializer, ContactLineSerializer, PasswordChangeSerializer


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'contacts': reverse('contact-list-detail', request=request, format=format),
    })


class UserListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(pk=self.request.user.pk)
        return queryset


class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ListCreateUserContactsAPIView(generics.ListCreateAPIView):
    serializer_class = ContactLineSerializer

    def get_queryset(self):
        queryset = ContactLine.objects.filter(contacts_list__owner=self.request.user).prefetch_related('contact')
        return queryset


class DeleteUserContactAPIView(generics.DestroyAPIView):

    def get_queryset(self):
        return ContactLine.objects.filter(contacts_list__owner=self.request.user)


class UserPasswordChangeAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = PasswordChangeSerializer
    permission_classes = (IsOwner, )


class UserCheckExistsAPIView(views.APIView):

    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('username')
        if username:
            if User.objects.filter(username=username).exists():
                return Response({"detail": f"'{username}' exists"},
                                status=status.HTTP_200_OK)
            else:
                return Response({"detail": f"'{username}' does not exists"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "The 'username' get parameter is not provided"},
                            status=status.HTTP_400_BAD_REQUEST)


class UserBlockAPIView(views.APIView):

    def post(self, request, *args, **kwargs):
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


class UserUnBlockAPIView(views.APIView):

    def post(self, request, *args, **kwargs):
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
