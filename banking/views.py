# banking/views.py

from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError 

from django.contrib.auth import authenticate, login
from .forms import LoginForm

from .forms import SignupForm, TransactionForm
from .models import Customer, Account, Transaction

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

def account_details(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    account = get_object_or_404(Account, customer=customer)
    return render(request, 'account_details.html', {'customer': customer, 'account': account})

def transaction_history(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    transactions = Transaction.objects.filter(account__customer=customer)
    return render(request, 'transaction_history.html', {'customer': customer, 'transactions': transactions})

def make_transaction(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    
    if request.method == 'POST':
        transaction_form = TransactionForm(request.POST)
        if transaction_form.is_valid():
            amount = transaction_form.cleaned_data['amount']
            transaction_type = transaction_form.cleaned_data['transaction_type']

            account = get_object_or_404(Account, customer=customer)

            if transaction_type == 'deposit':
                account.balance += amount
            elif transaction_type == 'withdraw':
                if amount <= account.balance:
                    account.balance -= amount
                else:
                    # Handle insufficient funds error
                    return render(request, 'make_transaction.html', {'customer': customer, 'error': 'Insufficient funds'})

            # Save the transaction
            Transaction.objects.create(account=account, amount=amount, transaction_type=transaction_type)
            
            # Update the account balance
            account.save()

            # Redirect to the account details page
            return redirect('account_details', customer_id=customer.id)
    else:
        transaction_form = TransactionForm()

    return render(request, 'make_transaction.html', {'customer': customer, 'transaction_form': transaction_form})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Extract data from the form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                # Try to create a new User
                user = User.objects.create_user(username=username, email=email, password=password)

                # If successful, create a new Customer
                customer = Customer.objects.create(user=user, name=name, email=email)

                # Create a corresponding account for the customer
                Account.objects.create(customer=customer, balance=0.0)

                # Redirect to the customer list or any other page
                return redirect('customer_list')

            except IntegrityError:
                # Handle the case where the username already exists
                form.add_error('username', 'This username is already taken. Please choose a different one.')

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