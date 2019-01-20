from django.contrib.auth.models import User

from rest_framework import serializers

from .models import ContactLine, ContactsList


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', )


class ContactLineSerializer(serializers.ModelSerializer):

    contact = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = ContactLine
        fields = ('id', 'contact', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # исключение имеющихся юзеров
        self.fields['contact'].queryset = User.objects.exclude(contact_lines__contacts_list__owner=self.context['request'].user)

    def save(self, **kwargs):
        user_contacts_list, _ = ContactsList.objects.get_or_create(owner=self.context['request'].user)
        return super().save(contacts_list=user_contacts_list, **kwargs)
