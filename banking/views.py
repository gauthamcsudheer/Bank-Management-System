# banking/views.py

import random
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError 

from django.views.decorators.csrf import csrf_protect

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from decimal import Decimal

from .forms import LoginForm, ManagerSignupForm

from .forms import SignupForm, DepositForm, WithdrawalForm, TransferForm
from .models import Customer, Account, Transaction, Manager

from django.contrib.auth.decorators import user_passes_test

from django.contrib import messages

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

@login_required
def account_details(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    
    # Check if the logged-in user matches the requested customer's user
    if request.user != customer.user:
        raise PermissionDenied("You don't have permission to view this account.")
    
    account = get_object_or_404(Account, customer=customer)
    return render(request, 'account_details.html', {'customer': customer, 'account': account})

def transaction_history(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    transactions = Transaction.objects.filter(account__customer=customer)
    return render(request, 'transaction_history.html', {'customer': customer, 'transactions': transactions})

def generate_unique_account_number():
    """
    Generate a unique 6-digit account number.
    """
    while True:
        account_number = random.randint(100000, 999999)
        if not Account.objects.filter(account_number=account_number).exists():
            return account_number

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract data from the form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            photo = form.cleaned_data['photo']

            if password == confirm_password:
                try:
                    # Try to create a new User
                    user = User.objects.create_user(username=username, email=email, password=password)

                    # If successful, create a new Customer
                    customer = Customer.objects.create(user=user, name=name, email=email, phone_number=phone_number)

                    # Generate a unique 6-digit account number
                    account_number = generate_unique_account_number()

                    # Set the photo if provided
                    if photo:
                        customer.photo = photo
                        customer.save()

                    # Create a corresponding account for the customer
                    Account.objects.create(customer=customer, account_number=account_number, balance=0.0)

                    # Redirect to the login page or any other page
                    return redirect('login')

                except IntegrityError:
                    # Handle the case where the username already exists
                    form.add_error('username', 'This username is already taken. Please choose a different one.')

            else:
                form.add_error('confirm_password', 'Passwords do not match. Please enter matching passwords.')

        # Include the form with errors in the context
        # even if there is a CSRF verification failure
        return render(request, 'signup.html', {'form': form})

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Authenticate user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Log in the user
                login(request, user)

                # Redirect to the account details of the logged-in customer
                return redirect('account_details', customer_id=user.customer.id)

            else:
                # Invalid credentials, show an error
                form.add_error(None, 'Invalid username or password.')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def make_deposit(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)

    if request.method == 'POST':
        deposit_form = DepositForm(request.POST)
        if deposit_form.is_valid():
            amount = deposit_form.cleaned_data['amount']

            account = get_object_or_404(Account, customer=customer)
            
            # Convert 'amount' to Decimal to ensure consistency
            amount = Decimal(amount)

            account.balance += amount
            account.save()

            # Save the transaction
            Transaction.objects.create(account=account, amount=amount, transaction_type='deposit')

            # Redirect to the account details page
            return redirect('account_details', customer_id=customer.id)
    else:
        deposit_form = DepositForm()

    template_name = 'make_deposit.html'
    return render(request, template_name, {'customer': customer, 'deposit_form': deposit_form})

@login_required
def make_withdrawal(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)

    if request.method == 'POST':
        withdrawal_form = WithdrawalForm(request.POST)
        if withdrawal_form.is_valid():
            amount = withdrawal_form.cleaned_data['amount']

            account = get_object_or_404(Account, customer=customer)

            # Convert 'amount' to Decimal to ensure consistency
            amount = Decimal(amount)

            if amount <= account.balance:
                account.balance -= amount
                account.save()

                # Save the transaction
                Transaction.objects.create(account=account, amount=amount, transaction_type='withdraw')

                # Redirect to the account details page
                return redirect('account_details', customer_id=customer.id)
            else:
                # Handle insufficient funds error
                error_message = 'Insufficient funds'
                return render(request, 'make_withdrawal.html', {'customer': customer, 'withdrawal_form': withdrawal_form, 'error': error_message})

    else:
        withdrawal_form = WithdrawalForm()

    template_name = 'make_withdrawal.html'
    return render(request, template_name, {'customer': customer, 'withdrawal_form': withdrawal_form})

@login_required
def make_transfer(request, customer_id):
    sender = get_object_or_404(Customer, pk=customer_id)

    if request.method == 'POST':
        transfer_form = TransferForm(request.POST)
        if transfer_form.is_valid():
            recipient_account_number = transfer_form.cleaned_data['recipient_account_number']
            amount = transfer_form.cleaned_data['amount']

            try:
                recipient_account = Account.objects.get(account_number=recipient_account_number)
                recipient_customer = recipient_account.customer

            except Account.DoesNotExist:
                error_message = f'Account with number "{recipient_account_number}" not found.'
                return render(request, 'make_transfer.html', {'sender': sender, 'transfer_form': transfer_form, 'error': error_message})

            if sender == recipient_customer:
                error_message = 'You cannot transfer money to yourself.'
                return render(request, 'make_transfer.html', {'sender': sender, 'transfer_form': transfer_form, 'error': error_message})

            sender_account = get_object_or_404(Account, customer=sender)
            if amount <= sender_account.balance:
                # Convert 'amount' to Decimal to ensure consistency
                amount = Decimal(amount)

                # Deduct the amount from the sender's account
                sender_account.balance -= amount
                sender_account.save()

                # Add the amount to the recipient's account
                recipient_account.balance += amount
                recipient_account.save()

                # Save the transaction for the sender
                Transaction.objects.create(account=sender_account, amount=amount, transaction_type='transfer_send')

                # Save the transaction for the recipient
                Transaction.objects.create(account=recipient_account, amount=amount, transaction_type='transfer_receive')

                return redirect('account_details', customer_id=sender.id)
            else:
                error_message = 'Insufficient funds to make the transfer.'
                return render(request, 'make_transfer.html', {'sender': sender, 'transfer_form': transfer_form, 'error': error_message})

    else:
        transfer_form = TransferForm()

    template_name = 'make_transfer.html'
    return render(request, template_name, {'sender': sender, 'transfer_form': transfer_form})
    



def manager_signup(request):
    if request.method == 'POST':
        form = ManagerSignupForm(request.POST)
        if form.is_valid():
            managerid = form.cleaned_data['managerid']
            password = form.cleaned_data['password']
            
            # Create a new User
            user = User.objects.create_user(username=managerid, password=password)

            # Create a new Manager
            manager = Manager.objects.create(user=user, managerid=managerid, password=password)

            messages.success(request, 'Manager account created successfully. You can now log in.')
            return redirect('manager_login')

    else:
        form = ManagerSignupForm()

    return render(request, 'manager_signup.html', {'form': form})

def manager_login(request):
    if request.method == 'POST':
        managerid = request.POST['managerid']
        password = request.POST['password']

        # Authenticate manager
        user = authenticate(request, username=managerid, password=password)

        if user is not None:
            # Log in the manager
            login(request, user)
            return redirect('manager_dashboard')
        else:
            messages.error(request, 'Invalid managerid or password.')

    return render(request, 'manager_login.html')

def customer_details(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    return render(request, 'customer_details.html', {'customer': customer})


@login_required
def manager_dashboard(request):
    if not request.user.is_manager:
        raise PermissionDenied("You don't have permission to view the manager dashboard.")

    customers = Customer.objects.all()
    return render(request, 'manager_dashboard.html', {'customers': customers})

def delete_customer(request, customer_id):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, pk=customer_id)

        # Deleting related data (e.g., accounts and transactions)
        customer.account.delete()

        # Delete the associated user from Django's User model
        user = customer.user
        user.delete()

        messages.success(request, 'Customer deleted successfully.')
        return redirect('manager_dashboard')

    return redirect('manager_dashboard')  # Redirect in case of GET request or invalid request