from django.contrib import admin

from . import models


class ContactLineInline(admin.TabularInline):
    model = models.ContactLine
    extra = 0


class ContactsListAdmin(admin.ModelAdmin):
    inlines = [ContactLineInline, ]


class BlackListLineInline(admin.TabularInline):
    model = models.BlackListLine
    extra = 0


class BlackListAdmin(admin.ModelAdmin):
    inlines = [BlackListLineInline, ]


admin.site.register(models.ContactsList, ContactsListAdmin)
admin.site.register(models.BlackList, BlackListAdmin)
