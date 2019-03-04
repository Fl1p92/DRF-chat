from django.db import models


class Chat(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='chats')
    users = models.ManyToManyField('auth.User')

    def __str__(self):
        return f"{self.owner.username} chat # {self.id}"
