from django.contrib.auth.models import User

from rest_framework import serializers

from .models import Chat


class ChatSerializer(serializers.ModelSerializer):

    users = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), many=True)

    class Meta:
        model = Chat
        fields = ('id', 'users')

    def save(self, **kwargs):
        return super().save(owner=self.context['request'].user, **kwargs)
