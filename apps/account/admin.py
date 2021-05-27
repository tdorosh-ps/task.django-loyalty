from django.contrib import admin

from .models import Account, Service, Client

admin.site.register(Account)
admin.site.register(Service)
admin.site.register(Client)
