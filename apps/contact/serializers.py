from django.contrib.auth.models import User

from rest_framework import serializers

from .models import ContactLine
from .models import ContactsList


class UserSerializer(serializers.HyperlinkedModelSerializer):

    contacts_list = serializers.HyperlinkedIdentityField(view_name='contactslist-detail')

    class Meta:
        model = User
        fields = ('url', 'username', 'contacts_list', )


class ContactLineSerializer(serializers.ModelSerializer):

    contact = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = ContactLine
        fields = ('contact', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact'].queryset = User.objects.exclude(contact_lines__contacts_list__owner=self.context['request'].user)

    def save(self, **kwargs):
        user_contacts_list, _ = ContactsList.objects.get_or_create(owner=self.context['request'].user)
        return super().save(contacts_list=user_contacts_list, **kwargs)
