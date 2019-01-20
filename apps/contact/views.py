from django.contrib.auth.models import User

from rest_framework import generics, permissions, status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import ContactLine
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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny, )


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
                return Response({"detail": f"'{username}' exists"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": f"'{username}' does not exists"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("The 'username' get parameter is not provided", status=status.HTTP_400_BAD_REQUEST)
