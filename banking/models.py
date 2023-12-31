# banking/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    def __str__(self):
        return self.name

class Account(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    account_number = models.PositiveIntegerField(unique=True)
    balance = models.DecimalField(default=0.0, max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])

    def __str__(self):
        return f"Account {self.account_number} - {self.customer.name}"

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10)  # 'deposit' or 'withdraw'
    timestamp = models.DateTimeField(auto_now_add=True)

class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    managerid = models.CharField(max_length=8, unique=True)  # e.g., '2103092'
    password = models.CharField(max_length=255)  # You should hash the passwords in a real-world scenario

    @property
    def is_manager(self):
        # Add any condition to identify managers, for example, a specific flag or attribute
        return True

# Add a custom manager to the User model
User.add_to_class("is_manager", property(lambda u: hasattr(u, 'manager')))