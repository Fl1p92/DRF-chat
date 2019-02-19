from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.chats.models import Chat
from apps.contact.models import BlackList, ContactsList


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
        # Since when creating a new user contacts and blocked lists are not created, I do it manually
        ContactsList.objects.create(owner=self.user_admin)
        BlackList.objects.create(owner=self.user_admin)

        self.client = APIClient()
        self.client.force_authenticate(self.user_admin)

    def test_user_list(self):
        response = self.client.get(reverse('user-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), User.objects.count())

    def test_user_detail(self):
        response = self.client.get(reverse('user-detail', kwargs={'pk': self.user_admin.pk}))
        invalid_response = self.client.get(reverse('user-detail', kwargs={'pk': User.objects.last().pk + 1}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(invalid_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_contact_list_detail_add_delete(self):
        path = reverse('contact-list')
        data = {'contact': self.user_test.username}
        invalid_data = {'adasd': 'teadast'}

        # add user to contacts
        self.assertEqual(self.user_admin.contacts_list.contact_lines.count(), 0)
        post_response = self.client.post(path, data, format='json')
        invalid_post_response = self.client.post(path, invalid_data, format='json')
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user_admin.contacts_list.contact_lines.count(), 1)
        self.assertEqual(post_response.data['contact'], self.user_test.username)
        self.assertEqual(invalid_post_response.status_code, status.HTTP_400_BAD_REQUEST)

        # display contacts
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data), self.user_admin.contacts_list.contact_lines.count())

        # delete user from contacts
        delete_response = self.client.delete(
            reverse('contact-detail', kwargs={'pk': self.user_admin.contacts_list.contact_lines.first().pk})
        )
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user_admin.contacts_list.contact_lines.count(), 0)

    def test_check_user_exists(self):
        # check existence user
        exists_response = self.client.get(reverse('user-check-exists'), {'username': self.user_admin.username})
        self.assertEqual(exists_response.status_code, status.HTTP_200_OK)
        self.assertEqual(exists_response.data, {"detail": f"'{self.user_admin.username}' exists."})
        self.assertTrue(User.objects.filter(username=self.user_admin.username).exists())

        # check not existence user
        not_exists_response = self.client.get(reverse('user-check-exists'), {'username': 'tester'})
        self.assertEqual(not_exists_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(not_exists_response.data, {"detail": "'tester' does not exists."})

        # bad get params
        bad_param_response = self.client.get(reverse('user-check-exists'), {'bad_param': self.user_admin.username})
        self.assertEqual(bad_param_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(bad_param_response.data, {"detail": "The 'username' get parameter is not provided."})

    def test_user_block(self):
        # initial contact and tests
        self.client.post(reverse('contact-list'), {'contact': self.user_test.username}, format='json')
        self.assertTrue(self.user_admin.contacts_list.contact_lines.filter(contact=self.user_test).exists())
        self.assertEqual(self.user_admin.contacts_list.contact_lines.count(), 1)
        self.assertEqual(self.user_admin.black_list.blacklist_lines.count(), 0)

        # block user from contacts
        block_contact_user_response = self.client.post(reverse('user-block', kwargs={'pk': self.user_test.pk}))
        self.assertEqual(block_contact_user_response.status_code, status.HTTP_200_OK)
        self.assertEqual(block_contact_user_response.data, {"detail": f"{self.user_test} is blocked."})
        self.assertFalse(self.user_admin.contacts_list.contact_lines.filter(contact=self.user_test).exists())
        self.assertEqual(self.user_admin.contacts_list.contact_lines.count(), 0)
        self.assertEqual(self.user_admin.black_list.blacklist_lines.count(), 1)

        # block user not from contacts
        block_user_response = self.client.post(reverse('user-block', kwargs={'pk': self.second_user_test.pk}))
        self.assertEqual(block_user_response.status_code, status.HTTP_200_OK)
        self.assertEqual(block_user_response.data, {"detail": f"{self.second_user_test} is blocked."})
        self.assertEqual(self.user_admin.black_list.blacklist_lines.count(), 2)

        # repeated blocking same user
        self.assertTrue(self.user_admin.black_list.blacklist_lines.filter(blocked_contact=self.second_user_test).exists())
        repeated_block_response = self.client.post(reverse('user-block', kwargs={'pk': self.second_user_test.pk}))
        self.assertEqual(repeated_block_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(repeated_block_response.data, {"detail": f"{self.second_user_test} is already blocked."})

        # block invalid user
        invalid_pk = User.objects.last().pk + 1
        invalid_user_block_response = self.client.post(reverse('user-block', kwargs={'pk': invalid_pk}))
        self.assertEqual(invalid_user_block_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid_user_block_response.data, {"detail": f"User 'pk' {invalid_pk} is invalid."})
        self.assertFalse(User.objects.filter(pk=invalid_pk).exists())

    def test_user_unblock(self):
        # initial blocks and tests
        self.client.post(reverse('user-block', kwargs={'pk': self.user_test.pk}))
        self.assertTrue(self.user_admin.black_list.blacklist_lines.filter(blocked_contact=self.user_test).exists())
        self.assertEqual(self.user_admin.black_list.blacklist_lines.count(), 1)

        # unblock user
        unblock_response = self.client.post(reverse('user-unblock', kwargs={'pk': self.user_test.pk}))
        self.assertEqual(unblock_response.status_code, status.HTTP_200_OK)
        self.assertEqual(unblock_response.data, {"detail": f"{self.user_test.username} is unblocked."})
        self.assertFalse(self.user_admin.black_list.blacklist_lines.filter(blocked_contact=self.user_test).exists())
        self.assertEqual(self.user_admin.black_list.blacklist_lines.count(), 0)

        # unblock invalid user
        invalid_pk = User.objects.last().pk + 1
        invalid_unblock_response = self.client.post(reverse('user-unblock', kwargs={'pk': invalid_pk}))
        self.assertEqual(invalid_unblock_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid_unblock_response.data, {"detail": f"Blocked user#{invalid_pk} does not exists."})
        self.assertFalse(self.user_admin.black_list.blacklist_lines.filter(blocked_contact__pk=invalid_pk).exists())


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
        self.assertEqual(self.user_admin.chats.count(), 0)

        # create chat
        create_chat_response = self.client.post(reverse('user-create-chat', kwargs={'pk': self.user_test.pk}))
        self.assertEqual(create_chat_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_chat_response.data, {"detail": f"Chat with {self.user_test} is created. ID # 1."})
        self.assertEqual(self.user_admin.chats.count(), 1)
        self.assertEqual(list(self.user_admin.chats.first().users.all()), list(User.objects.filter(Q(pk=self.user_admin.pk) |
                                                                                                   Q(pk=self.user_test.pk))))
        # create chat with invalid user
        invalid_pk = User.objects.last().pk + 1
        invalid_user_create_chat_response = self.client.post(reverse('user-create-chat', kwargs={'pk': invalid_pk}))
        self.assertEqual(invalid_user_create_chat_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid_user_create_chat_response.data, {"detail": f"User 'pk' {invalid_pk} is invalid."})
        self.assertFalse(User.objects.filter(pk=invalid_pk).exists())

        # create chat with same user
        self.assertTrue(Chat.objects.filter(owner=self.user_admin, users=self.user_test).exists())
        repeated_create_chat_response = self.client.post(reverse('user-create-chat', kwargs={'pk': self.user_test.pk}))
        self.assertEqual(repeated_create_chat_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(repeated_create_chat_response.data, {"detail": f"Chat with {self.user_test} is already exists."})

    def test_chats_list(self):
        # initial data
        self.client.post(reverse('user-create-chat', kwargs={'pk': self.user_test.pk}))
        self.client.post(reverse('user-create-chat', kwargs={'pk': self.second_user_test.pk}))
        self.assertEqual(self.user_admin.chats.count(), 2)

        # list of chats
        get_response = self.client.get(reverse('chat-list'))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data), self.user_admin.chats.count())

    def test_chat_destroy(self):
        # initial data
        self.client.post(reverse('user-create-chat', kwargs={'pk': self.user_test.pk}))
        self.assertEqual(Chat.objects.count(), 1)

        # delete chat
        delete_post = self.client.delete(reverse('chat-detail', kwargs={'pk': Chat.objects.first().pk}))
        self.assertEqual(delete_post.status_code, status.HTTP_204_NO_CONTENT)
