from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils import timezone

from rest_framework.test import APITestCase

from apps.contact.models import ContactLine, ContactsList, BlackList, BlackListLine
from apps.contact.serializers import UserSerializer, ContactLineSerializer


class ContactAPITests(APITestCase):

    def setUp(self):
        self.user_admin = User.objects.create_user(
            username='admin',
            password='admin_password'
        )
        self.user_test = User.objects.create_user(
            username='test',
            password='test'
        )
        self.second_user_test = User.objects.create_user(
            username='second_test',
            password='test'
        )
        black_list = BlackList.objects.create(owner=self.user_admin)
        BlackListLine.objects.create(blacklist=black_list, blocked_contact=self.second_user_test)

    def test_user_serializer(self):
        request = HttpRequest
        request.user = self.user_admin
        detail_serialize = UserSerializer(self.second_user_test, context={'request': request})
        self.assertEqual(detail_serialize.data, {
            'id': self.second_user_test.pk,
            'username': self.second_user_test.username,
            'blocked': True,
        })

        list_serialize = UserSerializer(
            User.objects.exclude(pk=self.user_admin.pk),
            many=True,
            context={'request': request}
        )
        self.assertEqual(list_serialize.data, [
            {'id': self.user_test.pk, 'username': self.user_test.username, 'blocked': False},
            {'id': self.second_user_test.pk, 'username': self.second_user_test.username, 'blocked': True},
        ])

    def test_contactline_serializer(self):
        request = HttpRequest
        request.user = self.user_admin

        self.assertEqual(ContactLine.objects.count(), 0)
        self.assertFalse(ContactsList.objects.filter(owner=self.user_admin).exists())

        # create new contact line
        object_deserialize = ContactLineSerializer(
            data={'contact': self.user_test.username},
            context={'request': request},
        )
        self.assertTrue(object_deserialize.is_valid())
        object_deserialize.save()
        self.assertTrue(ContactsList.objects.filter(owner=self.user_admin).exists())
        self.assertEqual(ContactLine.objects.count(), 1)
        self.assertEqual(object_deserialize.data['created_datetime'], timezone.localtime().strftime('%d.%m.%Y %H:%M:%S'))

        # try create contact line with owner of contacts
        owner_line = ContactLineSerializer(
            data={'contact': self.user_admin},
            context={'request': request},
        )
        self.assertFalse(owner_line.is_valid())
        self.assertEqual(owner_line.errors, {'contact': [f'Объект с username={self.user_admin.username} не существует.']})

        # try create contact line with blocked user
        blocked_line = ContactLineSerializer(
            data={'contact': self.second_user_test},
            context={'request': request},
        )
        self.assertFalse(blocked_line.is_valid())
        self.assertEqual(blocked_line.errors, {'contact': [f'Объект с username={self.second_user_test.username} не существует.']})

        # try create contact line with user which already in contacts
        exists_line = ContactLineSerializer(
            data={'contact': self.user_test},
            context={'request': request},
        )
        self.assertFalse(exists_line.is_valid())
        self.assertEqual(exists_line.errors, {'contact': [f'Объект с username={self.user_test.username} не существует.']})

        # list of contact lines
        list_serialize = ContactLineSerializer(
            self.user_admin.contacts_list.contact_lines.all(),
            many=True,
            context={'request': request},
        )
        self.assertEqual(list_serialize.data, [{'id': 1, 'contact': self.user_test.username}])
        self.assertEqual(len(list_serialize.data), self.user_admin.contacts_list.contact_lines.count())
