from django.contrib import admin
from .models import *


class MailingAdmin(admin.ModelAdmin):
    list_display = ('begin', 'end', 'filters', 'message')
    list_display_links = ('begin', 'end', 'filters', 'message')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('phone', 'operator_code', 'tag')
    list_display_links = ('phone', 'operator_code', 'tag')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'status', 'mailing', 'client')
    list_display_links = ('datetime', 'status', 'mailing', 'client')


admin.site.register(Mailing, MailingAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Message, MessageAdmin)
