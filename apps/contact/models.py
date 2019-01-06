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
