from django.db import models


class ContactsList(models.Model):
    owner = models.OneToOneField('auth.User', related_name='contacts_list', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.owner.username}`s contacts list"


class ContactLine(models.Model):
    contacts_list = models.ForeignKey('ContactsList', on_delete=models.CASCADE, related_name='contact_lines')
    contact = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='contact_lines')

    class Meta:
        unique_together = (
            ("contacts_list", "contact"),
        )

    def __str__(self):
        return f"{self.contact.username} # {self.id}"


class BlackList(models.Model):
    owner = models.OneToOneField('auth.User', related_name='black_list', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.owner.username}`s black list"


class BlackListLine(models.Model):
    blacklist = models.ForeignKey('BlackList', on_delete=models.CASCADE, related_name='blacklist_lines')
    blocked_contact = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='blacklist_lines')

    class Meta:
        unique_together = (
            ("blacklist", "blocked_contact"),
        )

    def __str__(self):
        return f"{self.blocked_contact.username} # {self.id}"
