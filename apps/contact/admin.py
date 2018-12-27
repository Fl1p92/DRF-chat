from django.contrib import admin

from . import models


class ContactLineInline(admin.TabularInline):
    model = models.ContactLine
    extra = 0


class ContactsListAdmin(admin.ModelAdmin):
    inlines = [ContactLineInline, ]


admin.site.register(models.ContactsList, ContactsListAdmin)
