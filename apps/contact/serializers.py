from django.contrib.auth.models import User

from rest_framework import serializers

from .models import ContactsList, ContactLine


class UserSerializer(serializers.HyperlinkedModelSerializer):

    contacts_list = serializers.HyperlinkedIdentityField(view_name='contactslist-detail')

    class Meta:
        model = User
        fields = ('url', 'username', 'contacts_list', )


class ContactLineSerializer(serializers.HyperlinkedModelSerializer):

    contact = UserSerializer()

    class Meta:
        model = ContactLine
        fields = ('contact', )


class ContactsListSerializer(serializers.ModelSerializer):

    contact_lines = ContactLineSerializer(many=True)

    class Meta:
        model = ContactsList
        fields = ('contact_lines', )
