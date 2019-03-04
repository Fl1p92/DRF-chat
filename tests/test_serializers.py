from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils import timezone

from rest_framework.test import APITestCase

from apps.contact.models import ContactLine, ContactsList, BlackList, BlackListLine
from apps.contact.serializers import UserSerializer, ContactLineSerializer, PasswordChangeSerializer


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
        self.request = HttpRequest
        self.request.user = self.user_admin

    def test_user_serializer(self):
        # user detail
        detail_serialize = UserSerializer(self.second_user_test, context={'request': self.request})
        self.assertEqual(detail_serialize.data, {
            'id': self.second_user_test.pk,
            'username': self.second_user_test.username,
            'blocked': True,
        })

        # user list
        list_serialize = UserSerializer(
            User.objects.exclude(pk=self.user_admin.pk),
            many=True,
            context={'request': self.request}
        )
        self.assertEqual(list_serialize.data, [
            {'id': self.user_test.pk, 'username': self.user_test.username, 'blocked': False},
            {'id': self.second_user_test.pk, 'username': self.second_user_test.username, 'blocked': True},
        ])

    def test_contactline_serializer(self):
        self.assertEqual(ContactLine.objects.count(), 0)
        self.assertFalse(ContactsList.objects.filter(owner=self.user_admin).exists())

        # create new contact line
        object_deserialize = ContactLineSerializer(
            data={'contact': self.user_test.username},
            context={'request': self.request},
        )
        self.assertTrue(object_deserialize.is_valid())
        object_deserialize.save()
        self.assertTrue(ContactsList.objects.filter(owner=self.user_admin).exists())
        self.assertEqual(ContactLine.objects.count(), 1)

        # test which periodically crashes
        self.assertEqual(object_deserialize.data['created_datetime'], timezone.localtime().strftime('%d.%m.%Y %H:%M:%S'))

        # try create contact line with owner of contacts
        owner_line = ContactLineSerializer(
            data={'contact': self.user_admin},
            context={'request': self.request},
        )
        self.assertFalse(owner_line.is_valid())
        self.assertEqual(owner_line.errors, {'contact': [f'Объект с username={self.user_admin.username} не существует.']})

        # try create contact line with blocked user
        blocked_line = ContactLineSerializer(
            data={'contact': self.second_user_test},
            context={'request': self.request},
        )
        self.assertFalse(blocked_line.is_valid())
        self.assertEqual(blocked_line.errors, {'contact': [f'Объект с username={self.second_user_test.username} не существует.']})

        # try create contact line with user which already in contacts
        exists_line = ContactLineSerializer(
            data={'contact': self.user_test},
            context={'request': self.request},
        )
        self.assertFalse(exists_line.is_valid())
        self.assertEqual(exists_line.errors, {'contact': [f'Объект с username={self.user_test.username} не существует.']})

        # list of contact lines
        list_serialize = ContactLineSerializer(
            self.user_admin.contacts_list.contact_lines.all(),
            many=True,
            context={'request': self.request},
        )
        self.assertEqual(list_serialize.data, [{'id': 1, 'contact': self.user_test.username}])
        self.assertEqual(len(list_serialize.data), self.user_admin.contacts_list.contact_lines.count())

    def test_password_change_serializer(self):
        valid_deserialize = PasswordChangeSerializer(
            instance=self.user_admin,
            data={'old_password': 'admin_password', 'new_password': 'new_pass', 'confirmed_password': 'new_pass', },
            context={'request': self.request},
        )
        self.assertTrue(valid_deserialize.is_valid())
        # ===========================================================================================
        # не уверен что это нужный тест, но не знаю как иначе можно проверить сменился пароль или нет
        instance = valid_deserialize.save()
        self.assertEqual(instance.password, User.objects.get(pk=self.user_admin.pk).password)
        # ===========================================================================================

        bad_old_password = PasswordChangeSerializer(
            instance=self.user_admin,
            data={'old_password': 'dfgdf', 'new_password': 'new_pass', 'confirmed_password': 'new_pass', },
            context={'request': self.request},
        )
        self.assertFalse(bad_old_password.is_valid())
        self.assertEqual(bad_old_password.errors, {'old_password': ['Wrong password.']})

        not_equals_passwords = PasswordChangeSerializer(
            instance=self.user_admin,
            data={'old_password': 'new_pass', 'new_password': 'pass', 'confirmed_password': 'not_pass', },
            context={'request': self.request},
        )
        self.assertFalse(not_equals_passwords.is_valid())
        self.assertEqual(not_equals_passwords.errors, {'non_field_errors': ['New password and confirmed password must be equal.']})

        no_different_new_password = PasswordChangeSerializer(
            instance=self.user_admin,
            data={'old_password': 'new_pass', 'new_password': 'new_pass', 'confirmed_password': 'new_pass', },
            context={'request': self.request},
        )
        self.assertFalse(no_different_new_password.is_valid())
        self.assertEqual(no_different_new_password.errors, {'non_field_errors': ['New password must be different from the old password.']})
