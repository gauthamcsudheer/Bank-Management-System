# banking/models.py

from django.db import models
from django.contrib.auth.models import User

from django.core.validators import MinValueValidator

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)


class Account(models.Model):
    customer = models.OneToOneField('Customer', on_delete=models.CASCADE)
    account_number = models.PositiveIntegerField(unique=True)
    balance = models.DecimalField(default=0.0, max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])

    def __str__(self):
        return f"Account {self.account_number} - {self.customer.name}"

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10)  # 'deposit' or 'withdraw'
    timestamp = models.DateTimeField(auto_now_add=True)
