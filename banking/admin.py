# banking/admin.py

from django.contrib import admin
from .models import Customer, Account, Transaction, Manager

admin.site.register(Customer)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Manager)