from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import ContactLine
from .permissions import IsContactsOwner
from .serializers import UserSerializer, ContactLineSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
    })


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserContacts(generics.ListCreateAPIView):
    serializer_class = ContactLineSerializer
    permission_classes = (IsContactsOwner, )

    def get_queryset(self):
        queryset = ContactLine.objects.filter(contacts_list__owner__pk=self.kwargs['pk']).prefetch_related('contact')
        return queryset
