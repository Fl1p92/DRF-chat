from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.chats.models import Chat


class ChatAPITests(APITestCase):

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

        self.client = APIClient()
        self.client.force_authenticate(self.user_admin)

    def test_chat_create(self):
        # initial test
        self.assertFalse(self.user_admin.chats.all().exists())

        # create chat
        create_chat_response = self.client.post(reverse('chat-create', kwargs={'pk': self.user_test.pk}))
        self.assertEqual(create_chat_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_chat_response.data, {"detail": f"Chat with {self.user_test} is created. ID # 1"})
        self.assertTrue(self.user_admin.chats.all().exists())
        self.assertEqual(list(self.user_admin.chats.first().users.all()), list(User.objects.filter(Q(pk=self.user_admin.pk) |
                                                                                                   Q(pk=self.user_test.pk))))
        # create chat with invalid user
        invalid_pk = User.objects.last().pk + 1
        invalid_user_create_chat_response = self.client.post(reverse('chat-create', kwargs={'pk': invalid_pk}))
        self.assertEqual(invalid_user_create_chat_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid_user_create_chat_response.data, {"detail": f"User 'pk' {invalid_pk} is invalid."})
        self.assertFalse(User.objects.filter(pk=invalid_pk).exists())

        # create chat with same user
        self.assertTrue(Chat.objects.filter(owner=self.user_admin, users=self.user_test).exists())
        repeated_create_chat_response = self.client.post(reverse('chat-create', kwargs={'pk': self.user_test.pk}))
        self.assertEqual(repeated_create_chat_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(repeated_create_chat_response.data, {"detail": f"Chat with {self.user_test} is already exists."})
