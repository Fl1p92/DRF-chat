from django.db import models


class ContactsList(models.Model):
    owner = models.OneToOneField('auth.User', related_name='contacts_list', on_delete=models.CASCADE)


class ContactLine(models.Model):
    contacts_list = models.ForeignKey('ContactsList', on_delete=models.CASCADE, related_name='contact_lines')
    contact = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ("contacts_list", "contact"),
        )
