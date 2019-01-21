from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from .models import ContactLine, ContactsList


class UserSerializer(serializers.ModelSerializer):

    blocked = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'blocked')

    def get_blocked(self, obj):
        return obj.blacklist_lines.filter(blacklist__owner=self.context['request'].user).exists()
        # return self.context['request'].user.black_list.blacklist_lines.filter(blocked_contact=obj).exists()  # depecated, +1 SQL request


class ContactLineSerializer(serializers.ModelSerializer):

    contact = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = ContactLine
        fields = ('id', 'contact', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # исключение имеющихся в contacts_list и заблокированных юзеров из предлагаемого списка контактов
        self.fields['contact'].queryset = User.objects.exclude(
            Q(pk=self.context['request'].user.pk) |
            Q(contact_lines__contacts_list__owner=self.context['request'].user) |
            Q(blacklist_lines__blacklist__owner=self.context['request'].user)
        )

    def save(self, **kwargs):
        user_contacts_list, _ = ContactsList.objects.get_or_create(owner=self.context['request'].user)
        self.fields.update(created_datetime=serializers.SerializerMethodField())
        return super().save(contacts_list=user_contacts_list, **kwargs)

    def get_created_datetime(self, obj):
        return timezone.localtime().strftime('%d.%m.%Y %H:%M:%S')


class PasswordChangeSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True, max_length=128)
    new_password = serializers.CharField(required=True, max_length=128)
    confirmed_password = serializers.CharField(required=True, max_length=128)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Wrong password.')
        return value

    def validate(self, data):
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirmed_password = data.get('confirmed_password')

        if confirmed_password != new_password:
            raise serializers.ValidationError('New password and confirmed password must be equal.')

        if old_password == new_password:
            raise serializers.ValidationError('New password must be different from the old password.')

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance

    @property
    def data(self):
        return ReturnDict({'detail': 'Success. Password changed'}, serializer=self)
