# banking/views.py

from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError 

from django.views.decorators.csrf import csrf_protect

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from .forms import LoginForm

from .forms import SignupForm, DepositForm, WithdrawalForm, TransferForm
from .models import Customer, Account, Transaction

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

def make_deposit(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)

    if request.method == 'POST':
        deposit_form = DepositForm(request.POST)
        if deposit_form.is_valid():
            amount = deposit_form.cleaned_data['amount']

            account = get_object_or_404(Account, customer=customer)
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

def make_withdrawal(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)

    if request.method == 'POST':
        withdrawal_form = WithdrawalForm(request.POST)
        if withdrawal_form.is_valid():
            amount = withdrawal_form.cleaned_data['amount']

            account = get_object_or_404(Account, customer=customer)

            if amount <= account.balance:
                account.balance -= amount
                account.save()

                # Save the transaction
                Transaction.objects.create(account=account, amount=amount, transaction_type='withdraw')

                # Redirect to the account details page
                return redirect('account_details', customer_id=customer.id)
            else:
                # Handle insufficient funds error
                return render(request, 'make_transaction.html', {'customer': customer, 'error': 'Insufficient funds'})

    else:
        withdrawal_form = WithdrawalForm()

    template_name = 'make_withdrawal.html'
    return render(request, template_name, {'customer': customer, 'withdrawal_form': withdrawal_form})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract data from the form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            photo = form.cleaned_data['photo']

            if password == confirm_password:
                try:
                    # Try to create a new User
                    user = User.objects.create_user(username=username, email=email, password=password)

                    # If successful, create a new Customer
                    customer = Customer.objects.create(user=user, name=name, email=email)

                    # Set the photo if provided
                    if photo:
                        customer.photo = photo
                        customer.save()

                    # Create a corresponding account for the customer
                    Account.objects.create(customer=customer, balance=0.0)

                    # Redirect to the customer list or any other page
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
def make_transfer(request, customer_id):
    sender = get_object_or_404(Customer, pk=customer_id)

    if request.method == 'POST':
        transfer_form = TransferForm(request.POST)
        if transfer_form.is_valid():
            recipient_username = transfer_form.cleaned_data['recipient_username']
            amount = transfer_form.cleaned_data['amount']

            try:
                # Get the recipient's user object
                recipient_user = User.objects.get(username=recipient_username)
                recipient_customer = Customer.objects.get(user=recipient_user)

            except User.DoesNotExist:
                # Handle the case where the username is not found
                error_message = f'User with username "{recipient_username}" not found.'
                return render(request, 'make_transfer.html', {'sender': sender, 'transfer_form': transfer_form, 'error': error_message})

            # Check if the logged-in user is not the same as the recipient
            if sender == recipient_customer:
                error_message = 'You cannot transfer money to yourself.'
                return render(request, 'make_transfer.html', {'sender': sender, 'transfer_form': transfer_form, 'error': error_message})

            # Check if the logged-in user has sufficient funds
            sender_account = get_object_or_404(Account, customer=sender)
            if amount <= sender_account.balance:
                # Deduct the amount from the sender's account
                sender_account.balance -= amount
                sender_account.save()

                # Add the amount to the recipient's account
                recipient_account = get_object_or_404(Account, customer=recipient_customer)
                recipient_account.balance += amount
                recipient_account.save()

                # Save the transaction for the sender
                Transaction.objects.create(account=sender_account, amount=amount, transaction_type='transfer_send')

                # Save the transaction for the recipient
                Transaction.objects.create(account=recipient_account, amount=amount, transaction_type='transfer_receive')

                # Redirect to the account details page for the sender
                return redirect('account_details', customer_id=sender.id)
            else:
                # Handle insufficient funds error
                error_message = 'Insufficient funds to make the transfer.'
                return render(request, 'make_transfer.html', {'sender': sender, 'transfer_form': transfer_form, 'error': error_message})

    else:
        transfer_form = TransferForm()

    template_name = 'make_transfer.html'
    return render(request, template_name, {'sender': sender, 'transfer_form': transfer_form})